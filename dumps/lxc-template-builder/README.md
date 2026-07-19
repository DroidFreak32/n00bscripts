# lxc-template-builder

Builds custom Proxmox LXC templates (Arch Linux, Debian) using Google Cloud
Build instead of a local Proxmox host, so you can update packages and bake
in your own package list without needing local Docker or spare capacity on
your PVE host.

Each distro is built from its **official upstream source** over HTTPS
(GPG/apt-signature verified) rather than Proxmox's own `download.proxmox.com`
template mirror, which is HTTP-only with no published checksums/signatures.

## How it works

Both pipelines follow the same shape:

1. Obtain a minimal root filesystem for the target distro (see per-distro
   notes below).
2. `docker import` it into a throwaway image.
3. Run a container from that image: update packages, install your chosen
   package list, run `scripts/<distro>.sh` (see below), clean up (package
   caches, `/etc/machine-id`, temp files).
4. `docker export` the container's filesystem back to a plain tarball.
5. Recompress with `zstd` and upload the result to a GCS bucket.

You then copy the resulting `.tar.zst` from GCS onto your Proxmox host's
template cache (`/var/lib/vz/template/cache/`) and `pct create` from it as
normal.

### Arch (`cloudbuild-arch.yaml`)

- Source: the official Arch bootstrap tarball from
  `geo.mirror.pkgbuild.com`, GPG-verified against Pierre Schmitz's
  release-signing key (fetched live via WKD, not a hardcoded fingerprint).
- The bootstrap tarball wraps everything in a `root.x86_64/` directory,
  which gets stripped before repackaging.
- `pacman`'s sandbox feature (Landlock-based) is disabled, since Cloud
  Build's runtime doesn't support Landlock.
- `/etc/pacman.d/mirrorlist` ships fully commented-out in the upstream
  bootstrap tarball, so a working HTTPS mirror is written explicitly.
- `pacman-key --init && pacman-key --populate archlinux` initializes the
  keyring, since the raw bootstrap tarball doesn't ship one populated.
- `console-getty.service` is explicitly enabled so `pct console` actually
  gets a login prompt.
- `systemd-firstboot.service` is masked. We deliberately strip
  `/etc/machine-id` (so every container cloned from the template gets its
  own unique ID), but current systemd's first-boot path tries to
  interactively prompt for a root password on `/dev/console` when it detects
  a genuine first boot, and that prompt hangs forever with nothing attached
  to answer it - masking it avoids the hang. `/etc/machine-id` still gets
  regenerated correctly on first real boot regardless, since that's handled
  by systemd's core startup, not by this unit.

### Debian (`cloudbuild-debian.yaml`)

- Source: `debootstrap --variant=minbase` run fresh against
  `https://deb.debian.org/debian` - no prebuilt template is downloaded at
  all, for a fully reproducible base.
- Runs in a sibling container with `--cap-add=SYS_ADMIN`, since
  `debootstrap`'s second stage needs to bind-mount `/proc` for package
  postinst scripts (a capability outside Docker's default set).
- Real device nodes debootstrap creates under `dev/` (`null`, `zero`,
  `tty`, etc., needed during the chrooted install) are stripped before
  repackaging - Proxmox's own extraction populates `/dev` itself and fails
  outright if it finds real device nodes already present in the archive.
- `--variant=minbase` excludes `Priority: important` packages, so
  `ifupdown`, `isc-dhcp-client`, and `systemd-sysv` are explicitly included:
  without `ifupdown`, `/etc/network/interfaces` never exists and Proxmox's
  post-create network setup hook fails outright; without
  `isc-dhcp-client`, DHCP networking silently doesn't work after boot;
  without `systemd-sysv`, there's no `/sbin/init` and the container fails
  to spawn at all.
- `dialog` is also baked into the base image (independent of whatever
  you put in `PACKAGES`).
- A `policy-rc.d` stub (`exit 101`) is dropped in during package
  installation and removed afterward, so `invoke-rc.d` doesn't try to
  actually start services against a container with no real init running as
  PID 1.

## Custom build-time scripts

`scripts/arch.sh` and `scripts/debian.sh` run *inside* the build container,
after packages are installed and before final cleanup - anything they
create (files, configs, users, etc.) becomes a permanent part of the baked
template image. This is **not** a container startup/cloud-init script; it
runs exactly once, at image build time, never again on the containers
cloned from the template.

Both ship as harmless no-ops by default (safe to leave as-is), and run
under `bash` (guaranteed present on both distros regardless of package
selection). The build fails if the script exits non-zero.

Since these scripts are local files (not fetched from a URL like everything
else in the pipeline), `submit-build.sh` submits the repo directory itself
as Cloud Build source (see `.gcloudignore` for what's excluded from that
upload - notably `build.env` and any stray `.tar`/`.tar.zst` files) instead
of using `--no-source`.

## Prerequisites

- [`gcloud` CLI](https://cloud.google.com/sdk/docs/install), authenticated
  and with a GCP project that has the Cloud Build API enabled.
- The Cloud Build service account
  (`<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com`) needs
  `roles/storage.objectAdmin` (or a narrower scoped equivalent) on the GCS
  bucket used for uploads.
- No local Docker install needed - everything runs inside Cloud Build.

## Repo layout

```
build.env              shared settings: PROJECT_ID, REGION, BUCKET (gitignored)
build.env.example       placeholder version of the above, copy to build.env

arch.env                Arch recipe: BASE_IMAGE, PACKAGES
debian.env              Debian recipe: DEBIAN_RELEASE, PACKAGES

cloudbuild-arch.yaml    Arch Cloud Build pipeline
cloudbuild-debian.yaml  Debian Cloud Build pipeline

scripts/arch.sh         custom build-time script, baked into the Arch image
scripts/debian.sh       custom build-time script, baked into the Debian image

submit-build.sh         entry point, driven by the DISTRO env var
.gcloudignore           excludes secrets/large files from the Cloud Build source upload
```

`arch.env`/`debian.env` hold no secrets (just package lists and version
info) and are committed directly - edit them in place and commit changes
like any other config. `build.env` holds your actual GCP project/bucket and
is gitignored; copy `build.env.example` to get started.

## Quick start

```bash
cp build.env.example build.env
$EDITOR build.env   # set PROJECT_ID, REGION, BUCKET

DISTRO=arch   ./submit-build.sh
DISTRO=debian ./submit-build.sh
```

`submit-build.sh` sources `build.env` plus `${DISTRO}.env` and submits
`cloudbuild-${DISTRO}.yaml` to Cloud Build with the right substitutions.
Adding a new distro means adding `<name>.env` +
`cloudbuild-<name>.yaml` - no script changes required.

## Getting the result onto Proxmox

```bash
gsutil cp gs://your-bucket/custom/<distro>-custom_YYYYMMDD-1_amd64.tar.zst \
  /var/lib/vz/template/cache/

pct create <vmid> local:vztmpl/<distro>-custom_YYYYMMDD-1_amd64.tar.zst \
  --hostname my-container \
  --memory 512 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --storage local-lvm \
  --unprivileged 1 \
  --password <root-password>
```

If `gsutil`/`gcloud` isn't installed on the PVE host, generate a signed URL
instead and `curl` it down:

```bash
gsutil signurl -d 1h /path/to/service-account.json \
  gs://your-bucket/custom/<file>.tar.zst
```

## Customizing

- Package list: edit `PACKAGES` in `arch.env` / `debian.env` (space-separated).
- Arch bootstrap version: `BASE_IMAGE` in `arch.env` - normally leave as-is,
  since `archlinux-bootstrap-x86_64.tar.zst` is a stable "latest" alias.
- Debian release: `DEBIAN_RELEASE` in `debian.env` (e.g. `trixie`, `bookworm`).
- Debian base size: `debootstrap --variant=minbase` in
  `cloudbuild-debian.yaml` produces a very small base; switch to
  `--variant=important` (or drop `--variant` entirely) for something closer
  to Proxmox's own "standard" template flavor.

## Known limitations

- Root password: neither pipeline bakes one in (Arch ships the account
  locked; Debian's default is whatever debootstrap sets, effectively no
  login). Set it via Proxmox itself at creation (`pct create ... --password`)
  or after (`pct set <vmid> --password ...`) - this is standard Proxmox
  behavior for any template, not specific to these pipelines.
- Everything is built and pushed as `amd64` - no multi-arch support.
