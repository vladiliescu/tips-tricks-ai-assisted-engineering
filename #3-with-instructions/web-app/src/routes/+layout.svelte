<script lang="ts">
    import "../app.css";
    import favicon from "$lib/assets/favicon.svg";

    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center">
                    <h1 class="text-xl font-semibold text-gray-900">
                        Predictive Analytics
                    </h1>
                </div>
                <div class="flex space-x-4">
                    <a
                        href="/"
                        class="text-gray-600 hover:text-gray-900 px-3 py-2"
                        >Dashboard</a
                    >
                    <a
                        href="/repositories"
                        class="text-gray-600 hover:text-gray-900 px-3 py-2"
                        >Repositories</a
                    >
                    <a
                        href="/teams"
                        class="text-gray-600 hover:text-gray-900 px-3 py-2"
                        >Teams</a
                    >
                    <a
                        href="/predict"
                        class="text-gray-600 hover:text-gray-900 px-3 py-2"
                        >Predict</a
                    >
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {@render children?.()}
    </main>
</div>
