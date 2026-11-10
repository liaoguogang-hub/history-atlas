plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.serialization")
}

android {
    namespace = "com.historyatlas.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.historyatlas.app"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.10.01")
    implementation(composeBom)

    // Core
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")

    // Compose
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    debugImplementation("androidx.compose.ui:ui-tooling")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.8.4")

    // JSON 解析（纯离线，无网络）
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")

    // 单元测试（纯 JVM）
    testImplementation("junit:junit:4.13.2")
    testImplementation(kotlin("test"))
}

/**
 * 把仓库根目录 `data/` 下的 JSON 同步到 assets。
 *
 * 用法：
 *   .\gradlew.bat :app:syncData
 *
 * 等价于仓库根目录的 `scripts\sync_data.ps1`，提供一条不依赖 shell 的同步入口。
 *
 * 源文件不存在时**只打印警告并跳过**，不会让构建失败——
 * 这样在数据文件尚未生成时也能正常编译 APK。
 */
val syncData by tasks.registering(Copy::class) {
    group = "build"
    description = "把 <repo>/data/*.json 复制到 app/src/main/assets/data/"

    // 可通过 -PsyncDataSource=<dir> / -PsyncDataTarget=<dir> 覆盖
    val defaultSource = rootProject.layout.projectDirectory.dir("../data")
    val defaultTarget = layout.projectDirectory.dir("src/main/assets/data")
    val sourceDir = (project.findProperty("syncDataSource") as String?)
        ?.let { file(it) }
        ?: defaultSource.asFile
    val targetDir = (project.findProperty("syncDataTarget") as String?)
        ?.let { file(it) }
        ?: defaultTarget.asFile

    from(sourceDir) {
        include("china.json", "world.json")
    }
    into(targetDir)

    // 源目录 / 源文件缺失时跳过，而不是报错
    onlyIf {
        val exists = sourceDir.isDirectory && listOf("china.json", "world.json").any {
            File(sourceDir, it).isFile
        }
        if (!exists) {
            logger.lifecycle(
                "[syncData] 警告：源数据不存在或为空（$sourceDir），跳过同步。" +
                    "构建将继续使用 assets 中已有的数据。"
            )
        }
        exists
    }

    doFirst {
        if (sourceDir.isDirectory) {
            listOf("china.json", "world.json").forEach { name ->
                val f = File(sourceDir, name)
                if (f.isFile) {
                    logger.lifecycle("[syncData] 同步 $name (${f.length()} 字节)")
                } else {
                    logger.lifecycle("[syncData] 警告：源文件不存在，跳过 $name（$sourceDir）")
                }
            }
        }
    }
}

/** 每次打包前自动同步一次数据，保证 APK 里始终是最新内容。 */
tasks.matching { it.name == "preBuild" }.configureEach {
    dependsOn(syncData)
}
