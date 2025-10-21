<script lang="ts">
    import { onMount } from "svelte";
    import {
        IconUsers,
        IconBrandGithub,
        IconBrain,
        IconChartBar,
        IconTrendingUp,
        IconClock,
        IconTarget,
        IconAlertTriangle,
    } from "@tabler/icons-svelte";

    // Mock data - in a real app, this would come from API calls
    let dashboardData = $state({
        teams: {
            total: 0,
            active: 0,
        },
        repositories: {
            total: 0,
            synced: 0,
        },
        predictions: {
            total: 0,
            validated: 0,
            accuracy: 0,
        },
        recentActivity: [],
        loading: true,
    });

    let stats = $derived([
        {
            name: "Active Teams",
            value: dashboardData.teams.active.toString(),
            change: "+2 this week",
            changeType: "positive",
            icon: IconUsers,
            color: "primary",
        },
        {
            name: "Repositories",
            value: dashboardData.repositories.total.toString(),
            change: `${dashboardData.repositories.synced} synced`,
            changeType: "neutral",
            icon: IconBrandGithub,
            color: "secondary",
        },
        {
            name: "Predictions Made",
            value: dashboardData.predictions.total.toString(),
            change: "+15 this week",
            changeType: "positive",
            icon: IconBrain,
            color: "success",
        },
        {
            name: "Avg. Accuracy",
            value: `${dashboardData.predictions.accuracy}%`,
            change: "+2.5% from last month",
            changeType: "positive",
            icon: IconTarget,
            color: "warning",
        },
    ]);

    async function loadDashboardData() {
        try {
            // Simulate API call
            await new Promise((resolve) => setTimeout(resolve, 1000));

            // Mock data
            dashboardData = {
                teams: {
                    total: 5,
                    active: 4,
                },
                repositories: {
                    total: 12,
                    synced: 8,
                },
                predictions: {
                    total: 156,
                    validated: 89,
                    accuracy: 73.5,
                },
                recentActivity: [
                    {
                        id: 1,
                        type: "prediction",
                        title: "New feature estimation completed",
                        description:
                            "Login system enhancement predicted at 8 story points",
                        time: "2 hours ago",
                        team: "Frontend Team",
                    },
                    {
                        id: 2,
                        type: "sync",
                        title: "Repository synchronized",
                        description:
                            "user-management-api successfully synced with 23 new issues",
                        time: "4 hours ago",
                        team: null,
                    },
                    {
                        id: 3,
                        type: "validation",
                        title: "Prediction validated",
                        description:
                            "API refactoring task completed in 5.2 hours (predicted 6.0)",
                        time: "1 day ago",
                        team: "Backend Team",
                    },
                    {
                        id: 4,
                        type: "team",
                        title: "New team member added",
                        description:
                            "Sarah Johnson joined the Frontend Team as Senior Developer",
                        time: "2 days ago",
                        team: "Frontend Team",
                    },
                ],
                loading: false,
            };
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            dashboardData.loading = false;
        }
    }

    onMount(() => {
        loadDashboardData();
    });

    function getActivityIcon(type: string) {
        switch (type) {
            case "prediction":
                return IconBrain;
            case "sync":
                return IconBrandGithub;
            case "validation":
                return IconTarget;
            case "team":
                return IconUsers;
            default:
                return IconChartBar;
        }
    }

    function getActivityColor(type: string) {
        switch (type) {
            case "prediction":
                return "text-primary-600 bg-primary-100";
            case "sync":
                return "text-secondary-600 bg-secondary-100";
            case "validation":
                return "text-success-600 bg-success-100";
            case "team":
                return "text-warning-600 bg-warning-100";
            default:
                return "text-gray-600 bg-gray-100";
        }
    }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="md:flex md:items-center md:justify-between">
            <div class="flex-1 min-w-0">
                <h2
                    class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate"
                >
                    Dashboard
                </h2>
                <p class="mt-1 text-sm text-gray-500">
                    Welcome back! Here's what's happening with your teams and
                    predictions.
                </p>
            </div>
            <div class="mt-4 flex md:mt-0 md:ml-4">
                <button
                    type="button"
                    class="btn-primary"
                    onclick={() => (window.location.href = "/predictions/new")}
                >
                    <IconBrain class="mr-2 h-4 w-4" />
                    New Prediction
                </button>
            </div>
        </div>
    </div>

    {#if dashboardData.loading}
        <!-- Loading skeleton -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {#each Array(4) as _}
                <div class="card">
                    <div class="skeleton h-6 w-24 mb-2"></div>
                    <div class="skeleton h-8 w-16 mb-1"></div>
                    <div class="skeleton h-4 w-32"></div>
                </div>
            {/each}
        </div>
    {:else}
        <!-- Stats grid -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {#each stats as stat}
                <div class="stat-card">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <p
                                class="text-sm font-medium text-gray-600 truncate"
                            >
                                {stat.name}
                            </p>
                            <p
                                class="mt-1 text-3xl font-semibold text-gray-900"
                            >
                                {stat.value}
                            </p>
                            <p class="mt-1 text-sm text-gray-500">
                                {stat.change}
                            </p>
                        </div>
                        <div class={`p-3 rounded-full bg-${stat.color}-100`}>
                            <svelte:component
                                this={stat.icon}
                                class={`h-6 w-6 text-${stat.color}-600`}
                            />
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    <!-- Main content grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Recent Activity -->
        <div class="lg:col-span-2">
            <div class="card">
                <div class="card-header">
                    <h3
                        class="text-lg font-medium text-gray-900 flex items-center"
                    >
                        <IconClock class="mr-2 h-5 w-5 text-gray-400" />
                        Recent Activity
                    </h3>
                </div>

                {#if dashboardData.loading}
                    <!-- Loading skeleton for activity -->
                    <div class="space-y-4">
                        {#each Array(4) as _}
                            <div class="flex items-start space-x-3">
                                <div
                                    class="skeleton h-10 w-10 rounded-full"
                                ></div>
                                <div class="flex-1">
                                    <div class="skeleton h-4 w-48 mb-2"></div>
                                    <div class="skeleton h-3 w-64 mb-1"></div>
                                    <div class="skeleton h-3 w-24"></div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="flow-root">
                        <ul class="-mb-8">
                            {#each dashboardData.recentActivity as activity, i}
                                <li>
                                    <div class="relative pb-8">
                                        {#if i !== dashboardData.recentActivity.length - 1}
                                            <span
                                                class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                                                aria-hidden="true"
                                            ></span>
                                        {/if}
                                        <div class="relative flex space-x-3">
                                            <div>
                                                <span
                                                    class={`h-8 w-8 rounded-full flex items-center justify-center ${getActivityColor(activity.type)}`}
                                                >
                                                    <svelte:component
                                                        this={getActivityIcon(
                                                            activity.type,
                                                        )}
                                                        class="h-4 w-4"
                                                    />
                                                </span>
                                            </div>
                                            <div class="flex-1 min-w-0">
                                                <div>
                                                    <p
                                                        class="text-sm font-medium text-gray-900"
                                                    >
                                                        {activity.title}
                                                    </p>
                                                    <p
                                                        class="mt-0.5 text-sm text-gray-500"
                                                    >
                                                        {activity.description}
                                                    </p>
                                                </div>
                                                <div
                                                    class="mt-2 flex items-center space-x-2 text-xs text-gray-500"
                                                >
                                                    <span>{activity.time}</span>
                                                    {#if activity.team}
                                                        <span>•</span>
                                                        <span
                                                            class="badge badge-gray"
                                                            >{activity.team}</span
                                                        >
                                                    {/if}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}
            </div>
        </div>

        <!-- Quick Actions & Status -->
        <div class="space-y-6">
            <!-- Quick Actions -->
            <div class="card">
                <div class="card-header">
                    <h3 class="text-lg font-medium text-gray-900">
                        Quick Actions
                    </h3>
                </div>
                <div class="space-y-3">
                    <a
                        href="/predictions/new"
                        class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div class="flex items-center">
                            <IconBrain class="h-5 w-5 text-primary-600 mr-3" />
                            <span class="text-sm font-medium text-gray-900"
                                >Create Prediction</span
                            >
                        </div>
                        <p class="mt-1 text-xs text-gray-500">
                            Estimate effort for a new task
                        </p>
                    </a>

                    <a
                        href="/repositories/sync"
                        class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div class="flex items-center">
                            <IconBrandGithub
                                class="h-5 w-5 text-secondary-600 mr-3"
                            />
                            <span class="text-sm font-medium text-gray-900"
                                >Sync Repository</span
                            >
                        </div>
                        <p class="mt-1 text-xs text-gray-500">
                            Import GitHub data
                        </p>
                    </a>

                    <a
                        href="/teams/new"
                        class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div class="flex items-center">
                            <IconUsers class="h-5 w-5 text-success-600 mr-3" />
                            <span class="text-sm font-medium text-gray-900"
                                >Add Team</span
                            >
                        </div>
                        <p class="mt-1 text-xs text-gray-500">
                            Create a new team
                        </p>
                    </a>

                    <a
                        href="/analytics"
                        class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div class="flex items-center">
                            <IconChartBar
                                class="h-5 w-5 text-warning-600 mr-3"
                            />
                            <span class="text-sm font-medium text-gray-900"
                                >View Analytics</span
                            >
                        </div>
                        <p class="mt-1 text-xs text-gray-500">
                            Team performance insights
                        </p>
                    </a>
                </div>
            </div>

            <!-- System Status -->
            <div class="card">
                <div class="card-header">
                    <h3 class="text-lg font-medium text-gray-900">
                        System Status
                    </h3>
                </div>
                <div class="space-y-3">
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">API Status</span>
                        <span class="badge badge-success">Online</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600"
                            >GitHub Integration</span
                        >
                        <span class="badge badge-success">Connected</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">ML Models</span>
                        <span class="badge badge-warning">Training</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">Database</span>
                        <span class="badge badge-success">Healthy</span>
                    </div>
                </div>
            </div>

            <!-- Alerts -->
            <div class="card">
                <div class="card-header">
                    <h3
                        class="text-lg font-medium text-gray-900 flex items-center"
                    >
                        <IconAlertTriangle
                            class="mr-2 h-5 w-5 text-warning-500"
                        />
                        Alerts
                    </h3>
                </div>
                <div class="space-y-3">
                    <div class="alert-warning">
                        <p class="text-sm">
                            <strong>Model Accuracy:</strong> Frontend Team predictions
                            below 70% threshold
                        </p>
                    </div>
                    <div class="alert-info">
                        <p class="text-sm">
                            <strong>Sync Required:</strong> 3 repositories need data
                            synchronization
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
