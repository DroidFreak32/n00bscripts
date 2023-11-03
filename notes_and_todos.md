#### Need to work on the namespaces and CustomSeekbarPreference

https://stackoverflow.com/questions/7119359/why-this-line-xmlnsandroid-http-schemas-android-com-apk-res-android-must-be

Issue:
```xml
    <com.lineageos.support.preferences.CustomSeekBarPreference
        android:key="gesture_anywhere_trigger_top"
        android:title="@string/trigger_top_title"
        android:defaultValue="0"
        android:max="99"
        settings:min="0"
        settings:units="%"
        android:dependency="gesture_anywhere_enabled" />
```

Here the `android:max` is recognized `settings:units` is undefined.
The namespace is defined here: https://github.com/DirtyUnicorns/android_vendor_support/blob/545a2c0d278f29569045e0e47b5a6f02c2d4a93a/src/com/dirtyunicorns/support/preferences/CustomSeekBarPreference.java#L40


#### Use AOSP Keys to sign boot.imgs  
https://forum.xda-developers.com/showpost.php?p=74473178&postcount=25


#### Print units in the new custome seekbarpreference
Preference: https://github.com/ROM-EXTRAS/android_vendor_support/commit/bed6a00422cb8d82f2098c40eb6c3bbacbccb4e6
File: res/xml/gesture_anywhere.xml



I7f0a56f1e2b4d65a595cbe8e9437963b0afa25ab
