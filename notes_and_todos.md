#### Need to get GA Added in lineage Parts.

```FATAL EXCEPTION: main
Process: org.lineageos.lineageparts, PID: 9267
java.lang.RuntimeException: Unable to start activity ComponentInfo{org.lineageos.lineageparts/org.lineageos.lineageparts.PartsActivity}: java.lang.UnsupportedOperationException: Unable to get part info: Intent { cmp=org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings (has extras) }
	at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:3270)
	at android.app.ActivityThread.handleLaunchActivity(ActivityThread.java:3409)
	at android.app.servertransaction.LaunchActivityItem.execute(LaunchActivityItem.java:83)
	at android.app.servertransaction.TransactionExecutor.executeCallbacks(TransactionExecutor.java:135)
	at android.app.servertransaction.TransactionExecutor.execute(TransactionExecutor.java:95)
	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:2016)
	at android.os.Handler.dispatchMessage(Handler.java:107)
	at android.os.Looper.loop(Looper.java:214)
	at android.app.ActivityThread.main(ActivityThread.java:7356)
	at java.lang.reflect.Method.invoke(Native Method)
	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:491)
	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:940)
Caused by: java.lang.UnsupportedOperationException: Unable to get part info: Intent { cmp=org.lineageos.lineageparts/gestures.gestureanywhere.GestureAnywhereSettings (has extras) }
	at org.lineageos.lineageparts.PartsActivity.onCreate(PartsActivity.java:106)
	at android.app.Activity.performCreate(Activity.java:7824)
	at android.app.Activity.performCreate(Activity.java:7813)
	at android.app.Instrumentation.callActivityOnCreate(Instrumentation.java:1306)
	at android.app.ActivityThread.performLaunchActivity(ActivityThread.java:3245)
	... 11 more
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
