<script lang="ts">
    import "../app.css";
    import { page } from "$app/stores";
    import {
        IconDashboard,
        IconUsers,
        IconBrandGithub,
        IconChartBar,
        IconBrain,
        IconSettings,
        IconMenu2,
        IconX,
        IconBell,
        IconSearch,
    } from "@tabler/icons-svelte";

    let { children } = $props();
    let sidebarOpen = $state(false);

    const navigation = [
        { name: "Dashboard", href: "/", icon: IconDashboard },
        { name: "Teams", href: "/teams", icon: IconUsers },
        { name: "Repositories", href: "/repositories", icon: IconBrandGithub },
        { name: "Predictions", href: "/predictions", icon: IconBrain },
        { name: "Analytics", href: "/analytics", icon: IconChartBar },
    ];

    function isCurrentPage(href: string): boolean {
        if (href === "/") {
            return $page.url.pathname === "/";
        }
        return $page.url.pathname.startsWith(href);
    }

    function closeSidebar() {
        sidebarOpen = false;
    }
</script>

<div class="min-h-screen bg-gray-50">
    <!-- Mobile sidebar backdrop -->
    {#if sidebarOpen}
        <div
            class="fixed inset-0 flex z-40 md:hidden"
            role="dialog"
            aria-modal="true"
        >
            <div
                class="fixed inset-0 bg-gray-600 bg-opacity-75"
                aria-hidden="true"
                onclick={closeSidebar}
            ></div>

            <!-- Mobile sidebar -->
            <div class="relative flex-1 flex flex-col max-w-xs w-full bg-white">
                <div class="absolute top-0 right-0 -mr-12 pt-2">
                    <button
                        type="button"
                        class="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                        onclick={closeSidebar}
                    >
                        <span class="sr-only">Close sidebar</span>
                        <IconX class="h-6 w-6 text-white" />
                    </button>
                </div>

                <div class="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
                    <div class="flex-shrink-0 flex items-center px-4">
                        <h1 class="text-xl font-bold gradient-text">
                            GitHub Analytics
                        </h1>
                    </div>
                    <nav class="mt-5 px-2 space-y-1">
                        {#each navigation as item}
                            <a
                                href={item.href}
                                class={isCurrentPage(item.href)
                                    ? "nav-link-active"
                                    : "nav-link-inactive"}
                                onclick={closeSidebar}
                            >
                                <svelte:component
                                    this={item.icon}
                                    class="mr-3 h-5 w-5"
                                />
                                {item.name}
                            </a>
                        {/each}
                    </nav>
                </div>

                <div class="flex-shrink-0 flex border-t border-gray-200 p-4">
                    <a href="/settings" class="nav-link-inactive w-full">
                        <IconSettings class="mr-3 h-5 w-5" />
                        Settings
                    </a>
                </div>
            </div>

            <div class="flex-shrink-0 w-14"></div>
        </div>
    {/if}

    <!-- Static sidebar for desktop -->
    <div class="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div
            class="flex-1 flex flex-col min-h-0 bg-white border-r border-gray-200"
        >
            <div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
                <div class="flex items-center flex-shrink-0 px-4">
                    <h1 class="text-xl font-bold gradient-text">
                        GitHub Analytics
                    </h1>
                </div>
                <nav class="mt-5 flex-1 px-2 space-y-1">
                    {#each navigation as item}
                        <a
                            href={item.href}
                            class={isCurrentPage(item.href)
                                ? "nav-link-active"
                                : "nav-link-inactive"}
                        >
                            <svelte:component
                                this={item.icon}
                                class="mr-3 h-5 w-5"
                            />
                            {item.name}
                        </a>
                    {/each}
                </nav>
            </div>

            <div class="flex-shrink-0 flex border-t border-gray-200 p-4">
                <a href="/settings" class="nav-link-inactive w-full">
                    <IconSettings class="mr-3 h-5 w-5" />
                    Settings
                </a>
            </div>
        </div>
    </div>

    <!-- Main content -->
    <div class="md:pl-64 flex flex-col flex-1">
        <!-- Top navigation bar -->
        <div
            class="sticky top-0 z-10 md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 bg-white border-b border-gray-200"
        >
            <button
                type="button"
                class="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                onclick={() => (sidebarOpen = !sidebarOpen)}
            >
                <span class="sr-only">Open sidebar</span>
                <IconMenu2 class="h-6 w-6" />
            </button>
        </div>

        <!-- Desktop top bar -->
        <div
            class="hidden md:flex md:items-center md:justify-between md:px-6 md:py-4 bg-white border-b border-gray-200"
        >
            <div class="flex-1 min-w-0">
                <!-- Search bar -->
                <div class="max-w-lg w-full lg:max-w-xs">
                    <label for="search" class="sr-only">Search</label>
                    <div class="relative">
                        <div
                            class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                        >
                            <IconSearch class="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            id="search"
                            name="search"
                            class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                            placeholder="Search..."
                            type="search"
                        />
                    </div>
                </div>
            </div>

            <div class="ml-4 flex items-center md:ml-6">
                <!-- Notifications -->
                <button
                    type="button"
                    class="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                    <span class="sr-only">View notifications</span>
                    <IconBell class="h-6 w-6" />
                </button>

                <!-- Profile dropdown placeholder -->
                <div class="ml-3 relative">
                    <div
                        class="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                        <span class="sr-only">Open user menu</span>
                        <div
                            class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center"
                        >
                            <span class="text-primary-600 text-sm font-medium"
                                >U</span
                            >
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Page content -->
        <main class="flex-1">
            <div class="py-6">
                {@render children?.()}
            </div>
        </main>
    </div>
</div>
