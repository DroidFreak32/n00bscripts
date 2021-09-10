#### Need to get GA Added in lineage Parts.

```07-29 00:54:03.727  1021  1518 I ActivityManager: Start proc 10742:org.lineageos.lineageparts/1000 for pre-top-activity {org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings}
07-29 00:54:03.743   266 10743 W zygote  : Reducing the number of considered missed Gc histogram windows from 1196 to 100
07-29 00:54:03.772  1021  2370 W OomAdjuster: Fallback pre-set sched group to default: not expected top priority
07-29 00:54:03.815 10742 10742 I os.lineagepart: The ClassLoaderContext is a special shared library.
07-29 00:54:03.818 10742 10742 D ApplicationLoaders: Returning zygote-cached class loader: /system/framework/android.hidl.base-V1.0-java.jar
07-29 00:54:03.821 10742 10742 I os.lineagepart: The ClassLoaderContext is a special shared library.
07-29 00:54:03.820 10742 10742 W os.lineageparts: type=1400 audit(0.0:271): avc: denied { write } for uid=1000 name="org.lineageos.lineageparts-A3FB7BitOkh6DyXXF5m_dw==" dev="mmcblk0p44" ino=56157 scontext=u:r:system_app:s0 tcontext=u:object_r:apk_data_file:s0 tclass=dir permissive=0
07-29 00:54:03.987 10742 10742 D PartsActivity: Launched with: Intent { cmp=org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings (has extras) } action: null component: gestures.gestureanywhere.GestureAnywhereSettings part: null fragment: null
07-29 00:54:04.000 10742 10742 D AndroidRuntime: Shutting down VM
07-29 00:54:04.001 10742 10742 E AndroidRuntime: FATAL EXCEPTION: main
07-29 00:54:04.001 10742 10742 E AndroidRuntime: Process: org.lineageos.lineageparts, PID: 10742
07-29 00:54:04.001 10742 10742 E AndroidRuntime: java.lang.RuntimeException: Unable to start activity ComponentInfo{org.lineageos.lineageparts/org.lineageos.lineageparts.PartsActivity}: java.lang.UnsupportedOperationException: Unable to get part info: Intent { cmp=org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings (has extras) }
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:3270)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.ActivityThread.handleLaunchActivity(ActivityThread.java:3409)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.servertransaction.LaunchActivityItem.execute(LaunchActivityItem.java:83)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.servertransaction.TransactionExecutor.executeCallbacks(TransactionExecutor.java:135)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.servertransaction.TransactionExecutor.execute(TransactionExecutor.java:95)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:2016)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.os.Handler.dispatchMessage(Handler.java:107)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.os.Looper.loop(Looper.java:214)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.ActivityThread.main(ActivityThread.java:7356)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at java.lang.reflect.Method.invoke(Native Method)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:491)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:940)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: Caused by: java.lang.UnsupportedOperationException: Unable to get part info: Intent { cmp=org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings (has extras) }
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at org.lineageos.lineageparts.PartsActivity.onCreate(PartsActivity.java:106)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.Activity.performCreate(Activity.java:7824)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.Activity.performCreate(Activity.java:7813)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.Instrumentation.callActivityOnCreate(Instrumentation.java:1306)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:3245)
07-29 00:54:04.001 10742 10742 E AndroidRuntime: 	... 11 more
07-29 00:54:04.008  1021  2370 W ActivityTaskManager:   Force finishing activity org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings
07-29 00:54:04.009  1021 10765 I DropBoxManagerService: add tag=system_app_crash isTagEnabled=true flags=0x2
07-29 00:54:04.016  1021  2370 W ActivityTaskManager:   Force finishing activity com.android.settings/.SubSettings
07-29 00:54:04.026  1021  1491 I ActivityManager: Showing crash dialog for package org.lineageos.lineageparts u0
07-29 00:54:04.513  1021  1493 W ActivityTaskManager: Activity top resumed state loss timeout for ActivityRecord{b27ed46 u0 org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings t29 f}
07-29 00:54:04.516  1021  1493 W ActivityTaskManager: Activity pause timeout for ActivityRecord{b27ed46 u0 org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings t29 f}
07-29 00:54:04.561  8856  8856 I chatty  : uid=1000(system) com.android.settings expire 2 lines
```

Currently parts are injected like so:
https://github.com/LineageOS/android_packages_apps_LineageParts/blob/lineage-17.1/AndroidManifest.xml#L116

I am able to ingest GA but unable to open it



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
