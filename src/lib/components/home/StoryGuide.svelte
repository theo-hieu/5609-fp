<script lang="ts">
  import type { Action } from 'svelte/action';
  import type { SceneCopy, SceneId } from '$lib/types';

  export let scenes: SceneCopy[] = [];
  export let activeScene: SceneId;
  export let observeScene: Action<HTMLElement, SceneId>;
</script>

<div class="py-8 lg:py-10">
  <div class="mb-8 max-w-2xl">
    <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Story Guide</p>
    <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Scroll the narrative to steer the dashboard.</h2>
    <p class="mt-4 text-sm leading-7 text-slate-300">
      Each block below activates a new scene. Season stays interactive throughout, while the story shifts the
      shot outcome lens when it needs to emphasize total volume or made-shot efficiency.
    </p>
  </div>

  <div class="space-y-8">
    {#each scenes as scene}
      <article
        use:observeScene={scene.id}
        class={[
          'panel flex min-h-[80vh] flex-col justify-center p-6 transition-all duration-500 sm:p-8',
          activeScene === scene.id
            ? 'border-amber-300/40 bg-slate-900/90 shadow-2xl shadow-amber-950/15'
            : 'border-white/10 bg-slate-900/55'
        ].join(' ')}
      >
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-amber-300/80">{scene.eyebrow}</p>
        <h3 class="mt-4 text-3xl font-black tracking-tight text-white sm:text-4xl">{scene.title}</h3>
        <p class="mt-4 max-w-2xl text-base leading-7 text-slate-200">{scene.description}</p>

        <div class="mt-8 space-y-5 text-sm leading-7 text-slate-300 sm:text-base">
          {#each scene.paragraphs as paragraph}
            <p>{paragraph}</p>
          {/each}
        </div>
      </article>
    {/each}
  </div>
</div>
