package com.scienceatlas.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.AppNavHost
import com.scienceatlas.app.ui.MainViewModel
import com.scienceatlas.app.ui.theme.ScienceAtlasTheme

/**
 * 应用入口。
 *
 * 采用单 Activity + Compose Navigation 结构：
 * - [MainViewModel] 持有地理 / 天文 / 物理 / 化学的分支切换状态
 * - [AppNavHost] 承载全部页面与导航
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val repository = ScienceRepository.getInstance(applicationContext)
        setContent {
            ScienceAtlasTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    ScienceApp(repository)
                }
            }
        }
    }
}

/**
 * App 根 Composable：绑定 ViewModel 与导航。
 */
@Composable
private fun ScienceApp(repository: ScienceRepository) {
    val viewModel: MainViewModel = viewModel(factory = MainViewModel.factory(repository))
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // 数据文件可达数 MB，必须在后台线程解析，避免阻塞首帧。
    LaunchedEffect(Unit) {
        repository.preloadAllAsync()
    }

    AppNavHost(
        repository = repository,
        scope = uiState.scope,
        onScopeChange = viewModel::setScope,
    )
}
