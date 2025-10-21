<script lang="ts">
	import { onMount } from 'svelte';

	let repositories = $state<
		Array<{
			id: number;
			name: string;
			url: string;
			owner: string;
			connected: boolean;
			lastSync: string;
		}>
	>([]);
	let loading = $state(true);
	let error = $state('');
	let showAddForm = $state(false);
	let newRepoUrl = $state('');
	let addingRepo = $state(false);

	const API_BASE = 'http://localhost:8000/api';

	async function fetchRepositories() {
		try {
			loading = true;
			error = '';
			const response = await fetch(`${API_BASE}/repositories`);
			if (response.ok) {
				const data = await response.json();
				repositories = data.repositories;
			} else {
				error = 'Failed to fetch repositories';
			}
		} catch (err) {
			error = `Unable to connect to backend: ${err instanceof Error ? err.message : 'Unknown error'}`;
		} finally {
			loading = false;
		}
	}

	async function addRepository(event: Event) {
		event.preventDefault();
		if (!newRepoUrl.trim()) return;

		try {
			addingRepo = true;
			// This would be a POST request in a real implementation
			// For now, just simulate success
			await new Promise((resolve) => setTimeout(resolve, 1000));

			// Add to local state (in real app, refetch from server)
			repositories = [
				...repositories,
				{
					id: Date.now(),
					name: newRepoUrl.split('/').pop() || newRepoUrl,
					url: newRepoUrl,
					owner: newRepoUrl.split('/').slice(-2)[0] || 'Unknown',
					connected: true,
					lastSync: new Date().toISOString()
				}
			];

			newRepoUrl = '';
			showAddForm = false;
		} catch (err) {
			error = `Failed to add repository: ${err instanceof Error ? err.message : 'Unknown error'}`;
		} finally {
			addingRepo = false;
		}
	}

	function removeRepository(id: number) {
		repositories = repositories.filter((repo) => repo.id !== id);
	}

	onMount(() => {
		fetchRepositories();
	});
</script>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="bg-white shadow-sm rounded-lg p-6">
		<div class="flex justify-between items-center">
			<div>
				<h1 class="text-2xl font-bold text-gray-900 mb-2">GitHub Repositories</h1>
				<p class="text-gray-600">Connect and manage repositories for effort estimation analysis</p>
			</div>
			<button onclick={() => (showAddForm = !showAddForm)} class="btn-primary">
				Add Repository
			</button>
		</div>
	</div>

	<!-- Add Repository Form -->
	{#if showAddForm}
		<div class="bg-white shadow-sm rounded-lg p-6">
			<h2 class="text-lg font-medium text-gray-900 mb-4">Connect New Repository</h2>
			<form onsubmit={addRepository} class="space-y-4">
				<div>
					<label for="repoUrl" class="label"> Repository URL </label>
					<input
						id="repoUrl"
						type="url"
						bind:value={newRepoUrl}
						placeholder="https://github.com/owner/repository"
						class="input-field"
						required
					/>
					<p class="text-sm text-gray-500 mt-1">Enter the full GitHub repository URL</p>
				</div>
				<div class="flex space-x-3">
					<button type="submit" class="btn-primary" disabled={addingRepo || !newRepoUrl.trim()}>
						{addingRepo ? 'Connecting...' : 'Connect Repository'}
					</button>
					<button type="button" onclick={() => (showAddForm = false)} class="btn-secondary">
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
					<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
				<div class="ml-3">
					<h3 class="text-sm font-medium text-red-800">Error</h3>
					<div class="mt-2 text-sm text-red-700">
						<p>{error}</p>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Repositories List -->
	<div class="bg-white shadow-sm rounded-lg overflow-hidden">
		{#if loading}
			<div class="p-8 text-center">
				<div
					class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
				></div>
				<p class="mt-2 text-gray-600">Loading repositories...</p>
			</div>
		{:else if repositories.length === 0}
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
						d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					/>
				</svg>
				<h3 class="mt-2 text-sm font-medium text-gray-900">No repositories connected</h3>
				<p class="mt-1 text-sm text-gray-500">
					Get started by connecting your first GitHub repository.
				</p>
				<div class="mt-6">
					<button onclick={() => (showAddForm = true)} class="btn-primary">
						Connect Repository
					</button>
				</div>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Repository
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Owner
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Status
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Last Sync
							</th>
							<th
								class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each repositories as repo (repo.id)}
							<tr>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<div class="flex-shrink-0 h-10 w-10">
											<div
												class="h-10 w-10 rounded-lg bg-gray-200 flex items-center justify-center"
											>
												<svg class="h-6 w-6 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
													<path
														fill-rule="evenodd"
														d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"
														clip-rule="evenodd"
													/>
												</svg>
											</div>
										</div>
										<div class="ml-4">
											<div class="text-sm font-medium text-gray-900">
												{repo.name}
											</div>
											<div class="text-sm text-gray-500">
												{repo.url}
											</div>
										</div>
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{repo.owner}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span
										class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {repo.connected
											? 'bg-green-100 text-green-800'
											: 'bg-red-100 text-red-800'}"
									>
										{repo.connected ? 'Connected' : 'Disconnected'}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{repo.lastSync ? new Date(repo.lastSync).toLocaleDateString() : 'Never'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<button
										onclick={() => removeRepository(repo.id)}
										class="text-red-600 hover:text-red-900"
									>
										Remove
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>

	<!-- Repository Stats -->
	{#if repositories.length > 0}
		<div class="bg-white shadow-sm rounded-lg p-6">
			<h2 class="text-lg font-medium text-gray-900 mb-4">Repository Statistics</h2>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div class="text-center">
					<div class="text-2xl font-bold text-blue-600">
						{repositories.length}
					</div>
					<div class="text-sm text-gray-500">Total Repositories</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-green-600">
						{repositories.filter((r) => r.connected).length}
					</div>
					<div class="text-sm text-gray-500">Connected</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-orange-600">
						{repositories.filter((r) => !r.connected).length}
					</div>
					<div class="text-sm text-gray-500">Disconnected</div>
				</div>
			</div>
		</div>
	{/if}
</div>
