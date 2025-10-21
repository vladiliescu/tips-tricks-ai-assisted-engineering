<script lang="ts">
    import { onMount } from "svelte";
    import {
        IconUsers,
        IconPlus,
        IconPencil,
        IconTrash,
        IconEye,
        IconChartBar,
        IconSearch,
        IconFilter,
    } from "@tabler/icons-svelte";
    import { teamsApi, type Team, formatApiError } from "$lib/api";

    let teams: Team[] = $state([]);
    let loading = $state(true);
    let error = $state("");
    let searchTerm = $state("");
    let showActiveOnly = $state(true);

    let filteredTeams = $derived(
        teams.filter((team) => {
            const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (team.description && team.description.toLowerCase().includes(searchTerm.toLowerCase()));
            const matchesActive = !showActiveOnly || team.is_active;
            return matchesSearch && matchesActive;
        })
    );

    async function loadTeams() {
        try {
            loading = true;
            error = "";
            teams = await teamsApi.listTeams(0, 1000, false); // Load all teams
        } catch (err) {
            error = formatApiError(err);
            console.error("Failed to load teams:", err);
        } finally {
            loading = false;
        }
    }

    async function deleteTeam(team: Team) {
        if (!confirm(`Are you sure you want to deactivate the team "${team.name}"?`)) {
            return;
        }

        try {
            await teamsApi.deleteTeam(team.id);
            await loadTeams(); // Refresh the list
        } catch (err) {
            error = formatApiError(err);
            console.error("Failed to delete team:", err);
        }
    }

    function getSeniorityBadgeColor(distribution: Record<string, number>): string {
        const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
        if (total === 0) return "gray";

        const seniorCount = (distribution.senior || 0) + (distribution.lead || 0) + (distribution.principal || 0);
        const seniorRatio = seniorCount / total;

        if (seniorRatio > 0.6) return "success";
        if (seniorRatio > 0.3) return "warning";
        return "error";
    }

    function formatSeniorityDistribution(distribution: Record<string, number>): string {
        const entries = Object.entries(distribution).filter(([_, count]) => count > 0);
        if (entries.length === 0) return "No members";
        return entries.map(([level, count]) => `${count} ${level}`).join(", ");
    }

    onMount(() => {
        loadTeams();
    });
</script>

<svelte:head>
    <title>Teams - GitHub Predictive Analytics</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="md:flex md:items-center md:justify-between">
            <div class="flex-1 min-w-0">
                <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                    Teams
                </h2>
                <p class="mt-1 text-sm text-gray-500">
                    Manage your development teams and track their performance
                </p>
            </div>
            <div class="mt-4 flex md:mt-0 md:ml-4">
                <a href="/teams/new" class="btn-primary">
                    <IconPlus class="mr-2 h-4 w-4" />
                    Add Team
                </a>
            </div>
        </div>
    </div>

    <!-- Filters and Search -->
    <div class="mb-6">
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div class="flex flex-col sm:flex-row gap-4">
                <!-- Search -->
                <div class="flex-1">
                    <label for="search" class="sr-only">Search teams</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <IconSearch class="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            id="search"
                            type="text"
                            bind:value={searchTerm}
                            class="input pl-10"
                            placeholder="Search teams by name or description..."
                        />
                    </div>
                </div>

                <!-- Filters -->
                <div class="flex items-center space-x-4">
                    <label class="inline-flex items-center">
                        <input
                            type="checkbox"
                            bind:checked={showActiveOnly}
                            class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                        />
                        <span class="ml-2 text-sm text-gray-700">Active only</span>
                    </label>
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

    <!-- Teams Grid -->
    {#if loading}
        <!-- Loading skeleton -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {#each Array(6) as _}
                <div class="card">
                    <div class="skeleton h-6 w-32 mb-4"></div>
                    <div class="skeleton h-4 w-full mb-2"></div>
                    <div class="skeleton h-4 w-3/4 mb-4"></div>
                    <div class="flex justify-between items-center">
                        <div class="skeleton h-6 w-16"></div>
                        <div class="skeleton h-8 w-24"></div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if filteredTeams.length === 0}
        <!-- Empty state -->
        <div class="text-center py-12">
            <IconUsers class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No teams found</h3>
            <p class="mt-1 text-sm text-gray-500">
                {teams.length === 0 ? "Get started by creating your first team." : "Try adjusting your search or filter criteria."}
            </p>
            {#if teams.length === 0}
                <div class="mt-6">
                    <a href="/teams/new" class="btn-primary">
                        <IconPlus class="mr-2 h-4 w-4" />
                        Add Team
                    </a>
                </div>
            {/if}
        </div>
    {:else}
        <!-- Teams grid -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {#each filteredTeams as team (team.id)}
                <div class="card hover:shadow-lg transition-shadow duration-200">
                    <!-- Team header -->
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex-1">
                            <h3 class="text-lg font-semibold text-gray-900">
                                {team.name}
                            </h3>
                            {#if team.description}
                                <p class="mt-1 text-sm text-gray-600 line-clamp-2">
                                    {team.description}
                                </p>
                            {/if}
                        </div>
                        <span class={`badge ${team.is_active ? 'badge-success' : 'badge-gray'}`}>
                            {team.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>

                    <!-- Team stats -->
                    <div class="space-y-3 mb-4">
                        <div class="flex items-center justify-between text-sm">
                            <span class="text-gray-600">Team Size</span>
                            <span class="font-medium">{team.current_size} members</span>
                        </div>

                        {#if team.average_velocity !== null}
                            <div class="flex items-center justify-between text-sm">
                                <span class="text-gray-600">Avg. Velocity</span>
                                <span class="font-medium">{team.average_velocity?.toFixed(1) || 'N/A'} pts/sprint</span>
                            </div>
                        {/if}

                        {#if team.estimation_accuracy_score !== null}
                            <div class="flex items-center justify-between text-sm">
                                <span class="text-gray-600">Estimation Accuracy</span>
                                <span class="font-medium">
                                    {team.estimation_accuracy_score ? `${(team.estimation_accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                                </span>
                            </div>
                        {/if}

                        {#if team.average_cycle_time_hours !== null}
                            <div class="flex items-center justify-between text-sm">
                                <span class="text-gray-600">Avg. Cycle Time</span>
                                <span class="font-medium">
                                    {team.average_cycle_time_hours ? `${team.average_cycle_time_hours.toFixed(1)}h` : 'N/A'}
                                </span>
                            </div>
                        {/if}
                    </div>

                    <!-- Team actions -->
                    <div class="flex items-center justify-between pt-4 border-t border-gray-200">
                        <div class="flex space-x-2">
                            <a
                                href="/teams/{team.id}"
                                class="text-primary-600 hover:text-primary-500 p-1 rounded"
                                title="View team details"
                            >
                                <IconEye class="h-4 w-4" />
                            </a>
                            <a
                                href="/teams/{team.id}/analytics"
                                class="text-success-600 hover:text-success-500 p-1 rounded"
                                title="View analytics"
                            >
                                <IconChartBar class="h-4 w-4" />
                            </a>
                            <a
                                href="/teams/{team.id}/edit"
                                class="text-warning-600 hover:text-warning-500 p-1 rounded"
                                title="Edit team"
                            >
                                <IconPencil class="h-4 w-4" />
                            </a>
                            {#if team.is_active}
                                <button
                                    onclick={() => deleteTeam(team)}
                                    class="text-error-600 hover:text-error-500 p-1 rounded"
                                    title="Deactivate team"
                                >
                                    <IconTrash class="h-4 w-4" />
                                </button>
                            {/if}
                        </div>

                        <span class="text-xs text-gray-500">
                            Created {new Date(team.created_at).toLocaleDateString()}
                        </span>
                    </div>
                </div>
            {/each}
        </div>
    {/if}

    <!-- Summary stats -->
    {#if !loading && teams.length > 0}
        <div class="mt-8 bg-gray-50 rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Team Summary</h3>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-primary-600">
                        {teams.length}
                    </div>
                    <div class="text-sm text-gray-600">Total Teams</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-success-600">
                        {teams.filter(t => t.is_active).length}
                    </div>
                    <div class="text-sm text-gray-600">Active Teams</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-secondary-600">
                        {teams.reduce((sum, team) => sum + team.current_size, 0)}
                    </div>
                    <div class="text-sm text-gray-600">Total Members</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-warning-600">
                        {teams.filter(t => t.estimation_accuracy_score && t.estimation_accuracy_score > 0.7).length}
                    </div>
                    <div class="text-sm text-gray-600">High-Performing Teams</div>
                </div>
            </div>
        </div>
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
