### avicii: crDroid FOD dim mode gets set to 0 when AOD is enabled
Steps to repro:
- Enable AOD
- Open LockScreen UI
- Wait for LockScreen to timeout and go back to AOD
- Notice the following in dmesg:

```logcat
09-07 21:29:31.734     0     0 E [20210907_21:29:31.734153]@2 [drm: notify_dim_store:2935] Notify dim not commit,send DSI_CMD_SET_HBM_ON_5 cmds
09-07 21:29:45.700     0     0 E         : [drm:dsi_display_set_power] *ERROR* [msm-dsi-error]: SDE_MODE_DPMS_LP1
09-07 21:29:45.700     0     0 E [20210907_21:29:45.700109]@0 [drm: dsi_panel_set_hbm_mode] *ERROR* [msm-dsi-error]: Send DSI_CMD_SET_HBM_OFF cmds.
09-07 21:29:45.700     0     0 E [20210907_21:29:45.700122]@0 [drm: dsi_panel_set_hbm_mode] *ERROR* [msm-dsi-error]: hbm_backight = 17, panel->bl_config.bl_level = 17
09-07 21:29:45.700     0     0 E [20210907_21:29:45.700131]@0 [drm: dsi_panel_update_backlight] *ERROR* [msm-dsi-error]: HBM is enabled
09-07 21:29:45.700     0     0 E [20210907_21:29:45.700139]@0 [drm: dsi_panel_set_hbm_mode] *ERROR* [msm-dsi-error]: Set HBM Mode = 0
```
