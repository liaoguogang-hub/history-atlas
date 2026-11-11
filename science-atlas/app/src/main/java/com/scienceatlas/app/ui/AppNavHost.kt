package com.scienceatlas.app.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.compositionLocalOf
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.scienceatlas.app.data.ScienceRepository
import com.scienceatlas.app.ui.screens.CompareScreen
import com.scienceatlas.app.ui.screens.EventDetailScreen
import com.scienceatlas.app.ui.screens.EventsScreen
import com.scienceatlas.app.ui.screens.FigureDetailScreen
import com.scienceatlas.app.ui.screens.FiguresScreen
import com.scienceatlas.app.ui.screens.HomeScreen
import com.scienceatlas.app.ui.screens.PeriodDetailScreen
import com.scienceatlas.app.ui.screens.SearchScreen
import com.scienceatlas.app.ui.screens.TimelineAxisScreen
import com.scienceatlas.app.ui.screens.TimelineTreeScreen

/**
 * 全局导航路由。
 *
 * scope 通过 query 参数传递，避免为四个 scope 各写一套图。
 */
object Routes {
    const val HOME = "home"
    const val TREE = "tree"
    const val AXIS = "axis"
    const val FIGURES = "figures"
    const val EVENTS = "events"
    const val SEARCH = "search"
    const val COMPARE = "compare"

    const val PERIOD = "period/{periodId}"
    const val EVENT = "event/{eventId}"
    const val FIGURE = "figure/{figureId}"

    fun period(id: String, scope: String) = "period/$id?scope=$scope"
    fun event(id: String, scope: String) = "event/$id?scope=$scope"
    fun figure(id: String, scope: String) = "figure/$id?scope=$scope"
}

/**
 * 当前 scope 的 CompositionLocal。
 *
 * 学科切换后，导航栈内所有页面共享该值，
 * 详情页因此能知道应该从哪个数据集取数据。
 */
val LocalScope = compositionLocalOf { ScienceRepository.SCOPE_GEO }

/**
 * App 根导航图。
 */
@Composable
fun AppNavHost(
    repository: ScienceRepository,
    scope: String,
    onScopeChange: (String) -> Unit,
    navController: NavHostController = rememberNavController(),
    viewModel: MainViewModel = viewModel(factory = MainViewModel.factory(repository)),
) {
    NavHost(
        navController = navController,
        startDestination = Routes.HOME,
    ) {
        composable(Routes.HOME) {
            HomeScreen(
                repository = repository,
                scope = scope,
                onScopeChange = onScopeChange,
                onOpenTree = { navController.navigate(Routes.TREE) },
                onOpenAxis = { navController.navigate(Routes.AXIS) },
                onOpenFigures = { navController.navigate(Routes.FIGURES) },
                onOpenEvents = { navController.navigate(Routes.EVENTS) },
                onOpenSearch = { navController.navigate(Routes.SEARCH) },
                onOpenCompare = { navController.navigate(Routes.COMPARE) },
            )
        }

        composable(Routes.TREE) {
            TimelineTreeScreen(
                repository = repository,
                scope = scope,
                onPeriodClick = { navController.navigate(Routes.period(it.id, scope)) },
                onSearch = { navController.navigate(Routes.SEARCH) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.AXIS) {
            TimelineAxisScreen(
                repository = repository,
                scope = scope,
                viewModel = viewModel,
                onEventClick = { navController.navigate(Routes.event(it.id, scope)) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.FIGURES) {
            FiguresScreen(
                repository = repository,
                scope = scope,
                onFigureClick = { navController.navigate(Routes.figure(it.id, scope)) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.EVENTS) {
            EventsScreen(
                repository = repository,
                scope = scope,
                onEventClick = { navController.navigate(Routes.event(it.id, scope)) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.SEARCH) {
            SearchScreen(
                repository = repository,
                scope = scope,
                onPeriodClick = { navController.navigate(Routes.period(it.id, scope)) },
                onEventClick = { navController.navigate(Routes.event(it.id, scope)) },
                onFigureClick = { navController.navigate(Routes.figure(it.id, scope)) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.COMPARE) {
            CompareScreen(
                repository = repository,
                scope = scope,
                onScopeChange = onScopeChange,
                onBack = { navController.popBackStack() },
            )
        }

        composable(
            route = Routes.PERIOD,
            arguments = listOf(
                navArgument("periodId") { type = NavType.StringType },
                navArgument("scope") { type = NavType.StringType; defaultValue = scope },
            ),
        ) { entry ->
            val periodId = entry.arguments?.getString("periodId").orEmpty()
            val periodScope = entry.arguments?.getString("scope") ?: scope
            PeriodDetailScreen(
                repository = repository,
                scope = periodScope,
                periodId = periodId,
                onEventClick = { navController.navigate(Routes.event(it.id, periodScope)) },
                onFigureClick = { navController.navigate(Routes.figure(it.id, periodScope)) },
                onChildPeriodClick = { navController.navigate(Routes.period(it.id, periodScope)) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(
            route = Routes.EVENT,
            arguments = listOf(
                navArgument("eventId") { type = NavType.StringType },
                navArgument("scope") { type = NavType.StringType; defaultValue = scope },
            ),
        ) { entry ->
            val eventId = entry.arguments?.getString("eventId").orEmpty()
            val eventScope = entry.arguments?.getString("scope") ?: scope
            EventDetailScreen(
                repository = repository,
                scope = eventScope,
                eventId = eventId,
                onFigureClick = { navController.navigate(Routes.figure(it.id, eventScope)) },
                onEventClick = { navController.navigate(Routes.event(it.id, eventScope)) },
                onPeriodClick = { navController.navigate(Routes.period(it.id, eventScope)) },
                onBack = { navController.popBackStack() },
            )
        }

        composable(
            route = Routes.FIGURE,
            arguments = listOf(
                navArgument("figureId") { type = NavType.StringType },
                navArgument("scope") { type = NavType.StringType; defaultValue = scope },
            ),
        ) { entry ->
            val figureId = entry.arguments?.getString("figureId").orEmpty()
            val figureScope = entry.arguments?.getString("scope") ?: scope
            FigureDetailScreen(
                repository = repository,
                scope = figureScope,
                figureId = figureId,
                onEventClick = { navController.navigate(Routes.event(it.id, figureScope)) },
                onFigureClick = { navController.navigate(Routes.figure(it.id, figureScope)) },
                onPeriodClick = { navController.navigate(Routes.period(it.id, figureScope)) },
                onBack = { navController.popBackStack() },
            )
        }
    }
}
