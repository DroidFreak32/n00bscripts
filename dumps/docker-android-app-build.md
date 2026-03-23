## Figuring out how to automatically build an android apk.

### Docker images

### Getting latest cmdline tools and setting up ANDROID_HOME:

I used the `mirror.gcr.io/gradle:9.4-jdk21-noble` image

```bash
# 1. Scrape the webpage for the latest Linux download URL
export ANDROID_HOME=/workspace/android-sdk
export LATEST_URL=$(curl -s https://developer.android.com/studio | grep -oE 'https://dl\.google\.com/android/repository/commandlinetools-linux-[0-9]+_latest\.zip' | head -n 1)

# 2. Download the zip file
curl -o cmdline-tools.zip "$LATEST_URL"

# 3. Create the required Android SDK directory structure
mkdir -p $ANDROID_HOME/cmdline-tools

# 4. Extract the zip into the cmdline-tools directory
unzip cmdline-tools.zip -d $ANDROID_HOME/cmdline-tools

# 5. Rename the extracted inner folder from 'cmdline-tools' to 'latest'
mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest

# 6. Set environment variables and verify it works
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin

yes | sdkmanager --licenses > /dev/null
```
