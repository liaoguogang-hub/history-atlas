package com.historyatlas.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.historyatlas.app.data.HistoryRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 全局 UI 状态。
 *
 * @param scope 当前历史分支：`china` 或 `world`。
 */
data class UiState(
    val scope: String = HistoryRepository.SCOPE_CHINA,
)

/**
 * 主 ViewModel：持有 scope 切换状态，其余数据由 Repository 按需提供。
 */
class MainViewModel(private val repository: HistoryRepository) : ViewModel() {

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    /**
     * 时间轴视窗（中心年份 + 每年像素宽度），按 scope 分别保存。
     *
     * 放在 ViewModel 而不是 Composable 内部，是为了在「时间轴 → 事件详情 → 返回」
     * 之后仍能回到用户已经拖动、缩放到的位置，而不是重置回初始视窗。
     */
    private val axisViewport = mutableMapOf<String, AxisViewport>()

    fun axisViewportOf(scope: String): AxisViewport? = axisViewport[scope]

    fun saveAxisViewport(scope: String, viewport: AxisViewport) {
        axisViewport[scope] = viewport
    }

    /** 切换历史分支，并预加载对应数据。 */
    fun setScope(scope: String) {
        if (_uiState.value.scope == scope) return
        _uiState.value = UiState(scope)
        repository.preload(scope)
    }

    companion object {
        fun factory(repository: HistoryRepository): ViewModelProvider.Factory = viewModelFactory {
            initializer { MainViewModel(repository) }
        }
    }
}

/** 时间轴视窗。centerYear 为屏幕中心的年份，pixelsPerYear 为缩放级别。 */
data class AxisViewport(val centerYear: Float, val pixelsPerYear: Float)
