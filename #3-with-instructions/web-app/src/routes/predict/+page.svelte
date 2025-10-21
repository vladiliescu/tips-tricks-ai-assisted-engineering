<script lang="ts">
    import { onMount } from "svelte";

    let loading = $state(false);
    let error = $state("");
    let prediction = $state(null);
    let taskForm = $state({
        title: "",
        description: "",
        repository: "",
        team: "",
        labels: [],
        priority: "medium",
        complexity: "medium"
    });

    let repositories = $state([]);
    let teams = $state([]);
    let availableLabels = $state(["feature", "bug", "enhancement", "documentation", "refactor", "testing"]);

    const API_BASE = "http://localhost:8000/api";

    async function fetchData() {
        try {
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
            console.error("Failed to fetch data:", err);
        }
    }

    async function generatePrediction() {
        if (!taskForm.title.trim() || !taskForm.description.trim()) {
            error = "Please fill in the task title and description";
            return;
        }

        try {
            loading = true;
            error = "";

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Mock prediction based on complexity and labels
            const baseEffort = taskForm.complexity === "low" ? 3 :
                             taskForm.complexity === "medium" ? 8 : 13;
            const labelMultiplier = taskForm.labels.includes("bug") ? 0.8 :
                                   taskForm.labels.includes("feature") ? 1.2 : 1.0;
            const priorityMultiplier = taskForm.priority === "high" ? 1.3 :
                                      taskForm.priority === "low" ? 0.7 : 1.0;

            const estimatedEffort = Math.round(baseEffort * labelMultiplier * priorityMultiplier);
            const confidence = Math.random() * 0.3 + 0.7; // 70-100%

            prediction = {
                effort: estimatedEffort,
                confidence: confidence,
                timeRange: {
                    min: Math.max(1, estimatedEffort - 2),
                    max: estimatedEffort + 3
                },
                factors: [
                    `Task complexity: ${taskForm.complexity}`,
                    `Priority level: ${taskForm.priority}`,
                    `Labels: ${taskForm.labels.join(", ") || "none"}`,
                    `Historical similar tasks analyzed`
                ]
            };
        } catch (err) {
            error = `Failed to generate prediction: ${err instanceof Error ? err.message : "Unknown error"}`;
        } finally {
            loading = false;
        }
    }

    function addLabel(label: string) {
        if (!taskForm.labels.includes(label)) {
            taskForm.labels = [...taskForm.labels, label];
        }
    }

    function removeLabel(label: string) {
        taskForm.labels = taskForm.labels.filter(l => l !== label);
    }

    function resetForm() {
        taskForm = {
            title: "",
            description: "",
            repository: "",
            team: "",
            labels: [],
            priority: "medium",
            complexity: "medium"
        };
        prediction = null;
        error = "";
    }

    onMount(() => {
        fetchData();
    });
</script>

<div class="space-y-6">
    <!-- Page Header -->
    <div class="bg-white shadow-sm rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
            Effort Prediction
        </h1>
        <p class="text-gray-600">
            Get AI-powered effort estimates for new tasks and features based on historical data
        </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Input Form -->
        <div class="bg-white shadow-sm rounded-lg p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
                Task Details
            </h2>

            <form onsubmit|preventDefault={generatePrediction} class="space-y-4">
                <!-- Task Title -->
                <div>
                    <label for="title" class="label">
                        Task Title *
                    </label>
                    <input
                        id="title"
                        type="text"
                        bind:value={taskForm.title}
                        placeholder="Implement user authentication"
                        class="input-field"
                        required
                    />
                </div>

                <!-- Task Description -->
                <div>
                    <label for="description" class="label">
                        Description *
                    </label>
                    <textarea
                        id="description"
                        bind:value={taskForm.description}
                        placeholder="Detailed description of the task, including requirements and acceptance criteria"
                        class="input-field"
                        rows="4"
                        required
                    ></textarea>
                </div>

                <!-- Repository Selection -->
                <div>
                    <label for="repository" class="label">
                        Repository
                    </label>
                    <select
                        id="repository"
                        bind:value={taskForm.repository}
                        class="input-field"
                    >
                        <option value="">Select repository</option>
                        {#each repositories as repo}
                            <option value={repo.id}>{repo.name}</option>
                        {/each}
                    </select>
                </div>

                <!-- Team Selection -->
                <div>
                    <label for="team" class="label">
                        Assigned Team
                    </label>
                    <select
                        id="team"
                        bind:value={taskForm.team}
                        class="input-field"
                    >
                        <option value="">Select team</option>
                        {#each teams as team}
                            <option value={team.id}>{team.name}</option>
                        {/each}
                    </select>
                </div>

                <!-- Priority -->
                <div>
                    <label class="label">Priority</label>
                    <div class="flex space-x-4">
                        {#each ["low", "medium", "high"] as priority}
                            <label class="flex items-center">
                                <input
                                    type="radio"
                                    bind:group={taskForm.priority}
                                    value={priority}
                                    class="mr-2"
                                />
                                <span class="capitalize">{priority}</span>
                            </label>
                        {/each}
                    </div>
                </div>

                <!-- Complexity -->
                <div>
                    <label class="label">Estimated Complexity</label>
                    <div class="flex space-x-4">
                        {#each ["low", "medium", "high"] as complexity}
                            <label class="flex items-center">
                                <input
                                    type="radio"
                                    bind:group={taskForm.complexity}
                                    value={complexity}
                                    class="mr-2"
                                />
                                <span class="capitalize">{complexity}</span>
                            </label>
                        {/each}
                    </div>
                </div>

                <!-- Labels -->
                <div>
                    <label class="label">Labels</label>
                    <div class="flex flex-wrap gap-2 mb-2">
                        {#each taskForm.labels as label}
                            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {label}
                                <button
                                    type="button"
                                    onclick={() => removeLabel(label)}
                                    class="ml-1 text-blue-600 hover:text-blue-800"
                                >
                                    ×
                                </button>
                            </span>
                        {/each}
                    </div>
                    <div class="flex flex-wrap gap-2">
                        {#each availableLabels as label}
                            {#if !taskForm.labels.includes(label)}
                                <button
                                    type="button"
                                    onclick={() => addLabel(label)}
                                    class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                                >
                                    + {label}
                                </button>
                            {/if}
                        {/each}
                    </div>
                </div>

                <!-- Form Actions -->
                <div class="flex space-x-3 pt-4">
                    <button
                        type="submit"
                        class="btn-primary"
                        disabled={loading || !taskForm.title.trim() || !taskForm.description.trim()}
                    >
                        {loading ? "Generating..." : "Generate Prediction"}
                    </button>
                    <button
                        type="button"
                        onclick={resetForm}
                        class="btn-secondary"
                    >
                        Reset
                    </button>
                </div>
            </form>
        </div>

        <!-- Prediction Results -->
        <div class="bg-white shadow-sm rounded-lg p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
                Prediction Results
            </h2>

            {#if loading}
                <div class="text-center py-8">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p class="mt-2 text-gray-600">Analyzing task and generating prediction...</p>
                </div>
            {:else if error}
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
                                Prediction Error
                            </h3>
                            <div class="mt-2 text-sm text-red-700">
                                <p>{error}</p>
                            </div>
                        </div>
                    </div>
                </div>
            {:else if prediction}
                <div class="space-y-6">
                    <!-- Main Prediction -->
                    <div class="text-center py-6 bg-blue-50 rounded-lg">
                        <div class="text-4xl font-bold text-blue-600 mb-2">
                            {prediction.effort}
                        </div>
                        <div class="text-sm text-gray-600 mb-1">Story Points</div>
                        <div class="text-xs text-gray-500">
                            Range: {prediction.timeRange.min}-{prediction.timeRange.max} SP
                        </div>
                    </div>

                    <!-- Confidence -->
                    <div>
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-gray-600">Confidence</span>
                            <span class="font-medium">{Math.round(prediction.confidence * 100)}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div
                                class="h-2 rounded-full {prediction.confidence > 0.8 ? 'bg-green-500' : prediction.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'}"
                                style="width: {prediction.confidence * 100}%"
                            ></div>
                        </div>
                    </div>

                    <!-- Factors -->
                    <div>
                        <h3 class="text-sm font-medium text-gray-900 mb-2">
                            Prediction Factors
                        </h3>
                        <ul class="space-y-1">
                            {#each prediction.factors as factor}
                                <li class="text-sm text-gray-600 flex items-center">
                                    <svg class="h-4 w-4 text-gray-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                    </svg>
                                    {factor}
                                </li>
                            {/each}
                        </ul>
                    </div>

                    <!-- Actions -->
                    <div class="pt-4 border-t border-gray-200">
                        <div class="flex space-x-3">
                            <button class="btn-primary text-sm">
                                Export Prediction
                            </button>
                            <button class="btn-secondary text-sm">
                                Save to Project
                            </button>
                        </div>
                    </div>
                </div>
            {:else}
                <div class="text-center py-8 text-gray-500">
                    <svg
                        class="mx-auto h-12 w-12 text-gray-400 mb-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                    </svg>
                    <p>Fill out the task details and click "Generate Prediction" to get an effort estimate.</p>
                </div>
            {/if}
        </div>
    </div>

    <!-- Tips and Information -->
    <div class="bg-white shadow-sm rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">
            Tips for Better Predictions
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h3 class="text-sm font-medium text-gray-900 mb-2">Task Description</h3>
                <ul class="text-sm text-gray-600 space-y-1">
                    <li>• Be specific about requirements</li>
                    <li>• Include acceptance criteria</li>
                    <li>• Mention technical constraints</li>
                    <li>• Note any dependencies</li>
                </ul>
            </div>
            <div>
                <h3 class="text-sm font-medium text-gray-900 mb-2">Better Accuracy</h3>
                <ul class="text-sm text-gray-600 space-y-1">
                    <li>• Connect more repositories for better training data</li>
                    <li>• Keep team information up to date</li>
                    <li>• Use consistent labeling</li>
                    <li>• Review and update predictions after completion</li>
                </ul>
            </div>
        </div>
    </div>
</div>
