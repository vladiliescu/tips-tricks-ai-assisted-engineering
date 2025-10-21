<script lang="ts">
    import { onMount } from "svelte";

    let healthStatus = $state({ status: "checking", service: "" });
    let repositories = $state([]);
    let teams = $state([]);
    let loading = $state(true);
    let error = $state("");

    const API_BASE = "http://localhost:8000/api";

    async function fetchData() {
        try {
            loading = true;
            error = "";

            // Fetch health status
            const healthResponse = await fetch(`${API_BASE}/health`);
            if (healthResponse.ok) {
                healthStatus = await healthResponse.json();
            }

            // Fetch repositories
            const reposResponse = await fetch(`${API_BASE}/repositories`);
            if (reposResponse.ok) {
                const reposData = await reposResponse.json();
                repositories = reposData.repositories;
            }

            // Fetch teams
            const teamsResponse = await fetch(`${API_BASE}/teams`);
            if (teamsResponse.ok) {
                const teamsData = await teamsResponse.json();
                teams = teamsData.teams;
            }
        } catch (err) {
            error = `Unable to connect to backend: ${err instanceof Error ? err.message : "Unknown error"}`;
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        fetchData();
    });
</script>

<div class="space-y-6">
    <!-- Page Header -->
    <div class="bg-white shadow-sm rounded-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">
            GitHub Effort Estimation Dashboard
        </h1>
        <p class="text-gray-600">
            Predictive analytics for project planning using GitHub data and team
            parameters
        </p>
    </div>

    <!-- System Status -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white shadow-sm rounded-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div
                        class="w-8 h-8 rounded-full {healthStatus.status ===
                        'healthy'
                            ? 'bg-green-500'
                            : 'bg-red-500'} flex items-center justify-center"
                    >
                        {#if healthStatus.status === "healthy"}
                            <svg
                                class="w-5 h-5 text-white"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                    clip-rule="evenodd"
                                ></path>
                            </svg>
                        {:else}
                            <svg
                                class="w-5 h-5 text-white"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clip-rule="evenodd"
                                ></path>
                            </svg>
                        {/if}
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">
                            Backend Status
                        </dt>
                        <dd
                            class="text-lg font-medium text-gray-900 capitalize"
                        >
                            {healthStatus.status}
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <div class="bg-white shadow-sm rounded-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div
                        class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center"
                    >
                        <svg
                            class="w-5 h-5 text-white"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                        >
                            <path
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            ></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">
                            Connected Repositories
                        </dt>
                        <dd class="text-lg font-medium text-gray-900">
                            {repositories.length}
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <div class="bg-white shadow-sm rounded-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div
                        class="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center"
                    >
                        <svg
                            class="w-5 h-5 text-white"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                        >
                            <path
                                d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"
                            ></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">
                            Active Teams
                        </dt>
                        <dd class="text-lg font-medium text-gray-900">
                            {teams.length}
                        </dd>
                    </dl>
                </div>
            </div>
        </div>
    </div>

    <!-- Error Display -->
    {#if error}
        <div class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg
                        class="h-5 w-5 text-red-400"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clip-rule="evenodd"
                        />
                    </svg>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">
                        Connection Error
                    </h3>
                    <div class="mt-2 text-sm text-red-700">
                        <p>{error}</p>
                        <p class="mt-1">
                            Make sure the backend is running on
                            http://localhost:8000
                        </p>
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- Quick Actions -->
    <div class="bg-white shadow-sm rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <a
                href="/repositories"
                class="btn-primary text-center no-underline"
            >
                Connect Repository
            </a>
            <a href="/teams" class="btn-secondary text-center no-underline">
                Manage Teams
            </a>
            <a href="/predict" class="btn-primary text-center no-underline">
                Create Prediction
            </a>
            <button
                onclick={fetchData}
                class="btn-secondary"
                disabled={loading}
            >
                {loading ? "Refreshing..." : "Refresh Data"}
            </button>
        </div>
    </div>

    <!-- Getting Started -->
    <div class="bg-white shadow-sm rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Getting Started</h2>
        <div class="prose prose-sm text-gray-600">
            <ol class="list-decimal list-inside space-y-2">
                <li>
                    Connect your GitHub repositories to start collecting data
                </li>
                <li>
                    Set up your team information including member roles and
                    experience
                </li>
                <li>
                    Allow the system to analyze historical data from your
                    repositories
                </li>
                <li>
                    Start creating effort predictions for new tasks and features
                </li>
            </ol>
        </div>
    </div>
</div>
