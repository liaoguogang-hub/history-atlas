# 历史图鉴 ProGuard/R8 规则

# kotlinx.serialization 生成的 serializer 需要保留
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**

-keepclassmembers class com.historyatlas.app.data.** {
    *** Companion;
}
-keepclasseswithmembers class com.historyatlas.app.data.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.historyatlas.app.data.**$$serializer { *; }

# 保留实体类字段（反序列化通过反射/构造器访问）
-keep class com.historyatlas.app.data.HistoryDataset { *; }
-keep class com.historyatlas.app.data.Period { *; }
-keep class com.historyatlas.app.data.Event { *; }
-keep class com.historyatlas.app.data.Figure { *; }
