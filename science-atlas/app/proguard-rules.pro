# 科学图鉴 ProGuard/R8 规则

# kotlinx.serialization 生成的 serializer 需要保留
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**

-keepclassmembers class com.scienceatlas.app.data.** {
    *** Companion;
}
-keepclasseswithmembers class com.scienceatlas.app.data.** {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class com.scienceatlas.app.data.**$$serializer { *; }

# 保留实体类字段（反序列化通过反射/构造器访问）
-keep class com.scienceatlas.app.data.ScienceDataset { *; }
-keep class com.scienceatlas.app.data.Period { *; }
-keep class com.scienceatlas.app.data.Event { *; }
-keep class com.scienceatlas.app.data.Figure { *; }
