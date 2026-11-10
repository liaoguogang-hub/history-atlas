package com.historyatlas.app

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
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.historyatlas.app.data.HistoryRepository
import com.historyatlas.app.ui.AppNavHost
import com.historyatlas.app.ui.MainViewModel
import com.historyatlas.app.ui.theme.HistoryAtlasTheme

/**
 * 应用入口。
 *
 * 采用单 Activity + Compose Navigation 结构：
 * - [MainViewModel] 持有中国史 / 世界史的分支切换状态
 * - [AppNavHost] 承载全部页面与导航
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val repository = HistoryRepository.getInstance(applicationContext)
        setContent {
            HistoryAtlasTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    HistoryApp(repository)
                }
            }
        }
    }
}

/**
 * App 根 Composable：绑定 ViewModel 与导航。
 */
@Composable
private fun HistoryApp(repository: HistoryRepository) {
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
