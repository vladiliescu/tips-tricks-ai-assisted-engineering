<script lang="ts">
    import { onMount } from "svelte";

    let teams = $state([]);
    let loading = $state(true);
    let error = $state("");
    let showAddForm = $state(false);
    let newTeam = $state({
        name: "",
        description: "",
        members: []
    });
    let addingTeam = $state(false);

    const API_BASE = "http://localhost:8000/api";

    async function fetchTeams() {
        try {
            loading = true;
            error = "";
            const response = await fetch(`${API_BASE}/teams`);
            if (response.ok) {
                const data = await response.json();
                teams = data.teams;
            } else {
                error = "Failed to fetch teams";
            }
        } catch (err) {
            error = `Unable to connect to backend: ${err instanceof Error ? err.message : "Unknown error"}`;
        } finally {
            loading = false;
        }
    }

    async function addTeam() {
        if (!newTeam.name.trim()) return;

        try {
            addingTeam = true;
            // This would be a POST request in a real implementation
            // For now, just simulate success
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Add to local state (in real app, refetch from server)
            teams = [...teams, {
                id: Date.now(),
                name: newTeam.name,
                description: newTeam.description,
                members: [],
                created: new Date().toISOString(),
                avgVelocity: 0,
                activeProjects: 0
            }];

            newTeam = { name: "", description: "", members: [] };
            showAddForm = false;
        } catch (err) {
            error = `Failed to add team: ${err instanceof Error ? err.message : "Unknown error"}`;
        } finally {
            addingTeam = false;
        }
    }

    function removeTeam(id: number) {
        teams = teams.filter(team => team.id !== id);
    }

    onMount(() => {
        fetchTeams();
    });
</script>

<div class="space-y-6">
    <!-- Page Header -->
    <div class="bg-white shadow-sm rounded-lg p-6">
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-gray-900 mb-2">
                    Development Teams
                </h1>
                <p class="text-gray-600">
                    Manage teams and their parameters for accurate effort estimation
                </p>
            </div>
            <button
                onclick={() => showAddForm = !showAddForm}
                class="btn-primary"
            >
                Add Team
            </button>
        </div>
    </div>

    <!-- Add Team Form -->
    {#if showAddForm}
        <div class="bg-white shadow-sm rounded-lg p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
                Create New Team
            </h2>
            <form onsubmit|preventDefault={addTeam} class="space-y-4">
                <div>
                    <label for="teamName" class="label">
                        Team Name
                    </label>
                    <input
                        id="teamName"
                        type="text"
                        bind:value={newTeam.name}
                        placeholder="Frontend Team"
                        class="input-field"
                        required
                    />
                </div>
                <div>
                    <label for="teamDescription" class="label">
                        Description
                    </label>
                    <textarea
                        id="teamDescription"
                        bind:value={newTeam.description}
                        placeholder="Brief description of the team's focus and responsibilities"
                        class="input-field"
                        rows="3"
                    ></textarea>
                </div>
                <div class="flex space-x-3">
                    <button
                        type="submit"
                        class="btn-primary"
                        disabled={addingTeam || !newTeam.name.trim()}
                    >
                        {addingTeam ? "Creating..." : "Create Team"}
                    </button>
                    <button
                        type="button"
                        onclick={() => showAddForm = false}
                        class="btn-secondary"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    {/if}

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
                        Error
                    </h3>
                    <div class="mt-2 text-sm text-red-700">
                        <p>{error}</p>
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- Teams List -->
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        {#if loading}
            <div class="p-8 text-center">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p class="mt-2 text-gray-600">Loading teams...</p>
            </div>
        {:else if teams.length === 0}
            <div class="p-8 text-center">
                <svg
                    class="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">
                    No teams created
                </h3>
                <p class="mt-1 text-sm text-gray-500">
                    Get started by creating your first development team.
                </p>
                <div class="mt-6">
                    <button
                        onclick={() => showAddForm = true}
                        class="btn-primary"
                    >
                        Create Team
                    </button>
                </div>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
                {#each teams as team}
                    <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-medium text-gray-900">
                                {team.name}
                            </h3>
                            <button
                                onclick={() => removeTeam(team.id)}
                                class="text-gray-400 hover:text-red-600"
                            >
                                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path
                                        fill-rule="evenodd"
                                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                        clip-rule="evenodd"
                                    />
                                </svg>
                            </button>
                        </div>

                        {#if team.description}
                            <p class="text-sm text-gray-600 mb-4">
                                {team.description}
                            </p>
                        {/if}

                        <div class="space-y-3">
                            <div class="flex justify-between items-center">
                                <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Members
                                </span>
                                <span class="text-sm font-medium text-gray-900">
                                    {team.members?.length || 0}
                                </span>
                            </div>

                            <div class="flex justify-between items-center">
                                <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Avg Velocity
                                </span>
                                <span class="text-sm font-medium text-gray-900">
                                    {team.avgVelocity || 0} SP
                                </span>
                            </div>

                            <div class="flex justify-between items-center">
                                <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Active Projects
                                </span>
                                <span class="text-sm font-medium text-gray-900">
                                    {team.activeProjects || 0}
                                </span>
                            </div>
                        </div>

                        <div class="mt-4 pt-4 border-t border-gray-200">
                            <div class="flex space-x-2">
                                <button class="btn-secondary text-xs px-3 py-1">
                                    Edit
                                </button>
                                <button class="btn-secondary text-xs px-3 py-1">
                                    Members
                                </button>
                                <button class="btn-secondary text-xs px-3 py-1">
                                    Analytics
                                </button>
                            </div>
                        </div>

                        <div class="mt-3 text-xs text-gray-500">
                            Created {team.created ? new Date(team.created).toLocaleDateString() : 'Unknown'}
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <!-- Team Stats -->
    {#if teams.length > 0}
        <div class="bg-white shadow-sm rounded-lg p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
                Team Overview
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">
                        {teams.length}
                    </div>
                    <div class="text-sm text-gray-500">Total Teams</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">
                        {teams.reduce((sum, team) => sum + (team.members?.length || 0), 0)}
                    </div>
                    <div class="text-sm text-gray-500">Total Members</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">
                        {teams.reduce((sum, team) => sum + (team.avgVelocity || 0), 0)}
                    </div>
                    <div class="text-sm text-gray-500">Combined Velocity</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-orange-600">
                        {teams.reduce((sum, team) => sum + (team.activeProjects || 0), 0)}
                    </div>
                    <div class="text-sm text-gray-500">Active Projects</div>
                </div>
            </div>
        </div>
    {/if}
</div>
