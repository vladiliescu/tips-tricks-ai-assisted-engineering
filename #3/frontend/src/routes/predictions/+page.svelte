<script lang="ts">
    import { onMount } from "svelte";
    import {
        IconBrain,
        IconPlus,
        IconCheck,
        IconClock,
        IconTarget,
        IconTrendingUp,
        IconFilter,
        IconSearch,
        IconEye,
        IconEdit,
    } from "@tabler/icons-svelte";
    import { predictionsApi, teamsApi, type Prediction, type Team, formatApiError } from "$lib/api";

    let predictions: Prediction[] = $state([]);
    let teams: Team[] = $state([]);
    let loading = $state(true);
    let error = $state("");
    let searchTerm = $state("");
    let selectedTeam = $state<number | null>(null);
    let selectedStatus = $state<string>("");
    let selectedType = $state<string>("");

    const statusOptions = [
        { value: "", label: "All Statuses" },
        { value: "pending", label: "Pending" },
        { value: "completed", label: "Completed" },
        { value: "validated", label: "Validated" },
        { value: "failed", label: "Failed" },
    ];

    const typeOptions = [
        { value: "", label: "All Types" },
        { value: "story_points", label: "Story Points" },
        { value: "hours", label: "Hours" },
        { value: "complexity", label: "Complexity" },
        { value: "risk_score", label: "Risk Score" },
    ];

    let filteredPredictions = $derived(
        predictions.filter((prediction) => {
            const matchesSearch = prediction.task_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (prediction.task_description && prediction.task_description.toLowerCase().includes(searchTerm.toLowerCase()));
            const matchesTeam = !selectedTeam || prediction.team_id === selectedTeam;
            const matchesStatus = !selectedStatus || prediction.status === selectedStatus;
            const matchesType = !selectedType || prediction.prediction_type === selectedType;

            return matchesSearch && matchesTeam && matchesStatus && matchesType;
        })
    );

    async function loadPredictions() {
        try {
            loading = true;
            error = "";
            const [predictionsData, teamsData] = await Promise.all([
                predictionsApi.listPredictions({ limit: 1000 }),
                teamsApi.listTeams(0, 1000, true)
            ]);
            predictions = predictionsData;
            teams = teamsData;
        } catch (err) {
            error = formatApiError(err);
            console.error("Failed to load predictions:", err);
        } finally {
            loading = false;
        }
    }

    function getStatusBadgeClass(status: string): string {
        switch (status) {
            case "pending":
                return "badge-warning";
            case "completed":
                return "badge-primary";
            case "validated":
                return "badge-success";
            case "failed":
                return "badge-error";
            default:
                return "badge-gray";
        }
    }

    function getTypeBadgeClass(type: string): string {
        switch (type) {
            case "story_points":
                return "badge-primary";
            case "hours":
                return "badge-success";
            case "complexity":
                return "badge-warning";
            case "risk_score":
                return "badge-error";
            default:
                return "badge-gray";
        }
    }

    function formatPredictionValue(value: number, type: string): string {
        switch (type) {
            case "story_points":
                return `${value} pts`;
            case "hours":
                return `${value.toFixed(1)}h`;
            case "complexity":
                return `${value.toFixed(1)}/10`;
            case "risk_score":
                return `${(value * 100).toFixed(0)}%`;
            default:
                return value.toString();
        }
    }

    function getTeamName(teamId: number | null): string {
        if (!teamId) return "No team";
        const team = teams.find(t => t.id === teamId);
        return team?.name || "Unknown team";
    }

    function formatConfidenceScore(score: number | null | undefined): string {
        if (!score) return "N/A";
        return `${(score * 100).toFixed(0)}%`;
    }

    onMount(() => {
        loadPredictions();
    });
</script>

<svelte:head>
    <title>Predictions - GitHub Predictive Analytics</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="md:flex md:items-center md:justify-between">
            <div class="flex-1 min-w-0">
                <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                    Predictions
                </h2>
                <p class="mt-1 text-sm text-gray-500">
                    AI-powered effort estimates for development tasks
                </p>
            </div>
            <div class="mt-4 flex space-x-3 md:mt-0 md:ml-4">
                <a href="/predictions/new" class="btn-primary">
                    <IconPlus class="mr-2 h-4 w-4" />
                    New Prediction
                </a>
            </div>
        </div>
    </div>

    <!-- Stats Cards -->
    {#if !loading && predictions.length > 0}
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div class="stat-card">
                <div class="flex items-center">
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-600">Total Predictions</p>
                        <p class="mt-1 text-3xl font-semibold text-gray-900">
                            {predictions.length}
                        </p>
                    </div>
                    <div class="p-3 rounded-full bg-primary-100">
                        <IconBrain class="h-6 w-6 text-primary-600" />
                    </div>
                </div>
            </div>

            <div class="stat-card">
                <div class="flex items-center">
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-600">Validated</p>
                        <p class="mt-1 text-3xl font-semibold text-gray-900">
                            {predictions.filter(p => p.status === 'validated').length}
                        </p>
                        <p class="text-sm text-gray-500">
                            {predictions.length > 0 ? Math.round((predictions.filter(p => p.status === 'validated').length / predictions.length) * 100) : 0}% rate
                        </p>
                    </div>
                    <div class="p-3 rounded-full bg-success-100">
                        <IconCheck class="h-6 w-6 text-success-600" />
                    </div>
                </div>
            </div>

            <div class="stat-card">
                <div class="flex items-center">
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-600">Pending</p>
                        <p class="mt-1 text-3xl font-semibold text-gray-900">
                            {predictions.filter(p => p.status === 'pending').length}
                        </p>
                    </div>
                    <div class="p-3 rounded-full bg-warning-100">
                        <IconClock class="h-6 w-6 text-warning-600" />
                    </div>
                </div>
            </div>

            <div class="stat-card">
                <div class="flex items-center">
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-600">Avg. Confidence</p>
                        <p class="mt-1 text-3xl font-semibold text-gray-900">
                            {predictions.length > 0 ?
                                Math.round((predictions.reduce((sum, p) => sum + (p.confidence_score || 0), 0) / predictions.length) * 100) : 0}%
                        </p>
                    </div>
                    <div class="p-3 rounded-full bg-secondary-100">
                        <IconTarget class="h-6 w-6 text-secondary-600" />
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- Filters -->
    <div class="mb-6">
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <!-- Search -->
                <div class="lg:col-span-2">
                    <label for="search" class="sr-only">Search predictions</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <IconSearch class="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            id="search"
                            type="text"
                            bind:value={searchTerm}
                            class="input pl-10"
                            placeholder="Search by task title or description..."
                        />
                    </div>
                </div>

                <!-- Team Filter -->
                <div>
                    <select bind:value={selectedTeam} class="input">
                        <option value={null}>All Teams</option>
                        {#each teams as team}
                            <option value={team.id}>{team.name}</option>
                        {/each}
                    </select>
                </div>

                <!-- Status Filter -->
                <div>
                    <select bind:value={selectedStatus} class="input">
                        {#each statusOptions as option}
                            <option value={option.value}>{option.label}</option>
                        {/each}
                    </select>
                </div>

                <!-- Type Filter -->
                <div>
                    <select bind:value={selectedType} class="input">
                        {#each typeOptions as option}
                            <option value={option.value}>{option.label}</option>
                        {/each}
                    </select>
                </div>
            </div>
        </div>
    </div>

    <!-- Error Alert -->
    {#if error}
        <div class="mb-6 alert-error">
            <p><strong>Error:</strong> {error}</p>
        </div>
    {/if}

    <!-- Predictions List -->
    {#if loading}
        <!-- Loading skeleton -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
                <div class="skeleton h-6 w-48"></div>
            </div>
            <div class="divide-y divide-gray-200">
                {#each Array(5) as _}
                    <div class="px-6 py-4">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <div class="skeleton h-5 w-64 mb-2"></div>
                                <div class="skeleton h-4 w-96 mb-2"></div>
                                <div class="flex items-center space-x-4">
                                    <div class="skeleton h-4 w-20"></div>
                                    <div class="skeleton h-4 w-16"></div>
                                    <div class="skeleton h-4 w-24"></div>
                                </div>
                            </div>
                            <div class="ml-4">
                                <div class="skeleton h-8 w-20"></div>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    {:else if filteredPredictions.length === 0}
        <!-- Empty state -->
        <div class="text-center py-12">
            <IconBrain class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No predictions found</h3>
            <p class="mt-1 text-sm text-gray-500">
                {predictions.length === 0 ? "Get started by creating your first prediction." : "Try adjusting your search or filter criteria."}
            </p>
            {#if predictions.length === 0}
                <div class="mt-6">
                    <a href="/predictions/new" class="btn-primary">
                        <IconPlus class="mr-2 h-4 w-4" />
                        New Prediction
                    </a>
                </div>
            {/if}
        </div>
    {:else}
        <!-- Predictions table -->
        <div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 class="text-lg font-medium text-gray-900">
                    {filteredPredictions.length} Prediction{filteredPredictions.length !== 1 ? 's' : ''}
                </h3>
            </div>

            <div class="divide-y divide-gray-200">
                {#each filteredPredictions as prediction (prediction.id)}
                    <div class="px-6 py-4 hover:bg-gray-50 transition-colors">
                        <div class="flex items-start justify-between">
                            <div class="flex-1 min-w-0">
                                <!-- Task title -->
                                <h4 class="text-sm font-medium text-gray-900 truncate">
                                    {prediction.task_title}
                                </h4>

                                <!-- Task description -->
                                {#if prediction.task_description}
                                    <p class="mt-1 text-sm text-gray-600 line-clamp-2">
                                        {prediction.task_description}
                                    </p>
                                {/if}

                                <!-- Metadata -->
                                <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-500">
                                    <div class="flex items-center">
                                        <span class="mr-1">Team:</span>
                                        <span class="font-medium">{getTeamName(prediction.team_id)}</span>
                                    </div>

                                    <div class="flex items-center">
                                        <span class="mr-1">Model:</span>
                                        <span class="font-medium">{prediction.model_name || 'Unknown'}</span>
                                    </div>

                                    <div class="flex items-center">
                                        <span class="mr-1">Created:</span>
                                        <span class="font-medium">
                                            {new Date(prediction.created_at).toLocaleDateString()}
                                        </span>
                                    </div>

                                    <div class="flex items-center">
                                        <span class="mr-1">Confidence:</span>
                                        <span class="font-medium">
                                            {formatConfidenceScore(prediction.confidence_score)}
                                        </span>
                                    </div>
                                </div>

                                <!-- Badges -->
                                <div class="mt-3 flex items-center space-x-2">
                                    <span class={`badge ${getStatusBadgeClass(prediction.status)}`}>
                                        {prediction.status.charAt(0).toUpperCase() + prediction.status.slice(1)}
                                    </span>

                                    <span class={`badge ${getTypeBadgeClass(prediction.prediction_type)}`}>
                                        {prediction.prediction_type.replace('_', ' ')}
                                    </span>
                                </div>
                            </div>

                            <!-- Prediction value and actions -->
                            <div class="ml-4 flex flex-col items-end">
                                <div class="text-right mb-2">
                                    <div class="text-2xl font-bold text-gray-900">
                                        {formatPredictionValue(prediction.predicted_value, prediction.prediction_type)}
                                    </div>
                                    {#if prediction.confidence_interval_lower && prediction.confidence_interval_upper}
                                        <div class="text-xs text-gray-500">
                                            {formatPredictionValue(prediction.confidence_interval_lower, prediction.prediction_type)} -
                                            {formatPredictionValue(prediction.confidence_interval_upper, prediction.prediction_type)}
                                        </div>
                                    {/if}
                                </div>

                                <div class="flex space-x-2">
                                    <a
                                        href="/predictions/{prediction.id}"
                                        class="text-primary-600 hover:text-primary-500 p-1 rounded"
                                        title="View details"
                                    >
                                        <IconEye class="h-4 w-4" />
                                    </a>

                                    {#if prediction.status === 'completed' || prediction.status === 'pending'}
                                        <a
                                            href="/predictions/{prediction.id}/validate"
                                            class="text-success-600 hover:text-success-500 p-1 rounded"
                                            title="Validate prediction"
                                        >
                                            <IconCheck class="h-4 w-4" />
                                        </a>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Pagination placeholder -->
        {#if filteredPredictions.length >= 50}
            <div class="mt-6 flex justify-center">
                <div class="text-sm text-gray-500">
                    Showing {filteredPredictions.length} predictions
                    <!-- Add pagination controls here if needed -->
                </div>
            </div>
        {/if}
    {/if}
</div>

<style>
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>
