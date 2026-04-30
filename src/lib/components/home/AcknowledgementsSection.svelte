<script lang="ts">
  type CreditLink = {
    label: string;
    href: string;
  };

  type CreditGroup = {
    title: string;
    items: string[];
    links?: CreditLink[];
  };

  const teamMembers = ['Aaron Castle', 'Sanketh Kodimala', 'Theo Nguyen'];

  const creditGroups: CreditGroup[] = [
    {
      title: 'Dataset',
      items: [
        'Mexwell NBA Shots, Kaggle. NBA regular-season shot location data, 2003-04 through 2023-24.',
        'Metadata license: "Other (specified in description)." Photo acknowledgement: TJ Dragotta on Unsplash.'
      ],
      links: [{ label: 'mexwell/nba-shots', href: 'https://www.kaggle.com/datasets/mexwell/nba-shots' }]
    },
    {
      title: '3D Models and Images',
      items: [
        'Houston Rockets Basketball Stadium by alplaleli, Sketchfab.',
        'Basketball by Marek Picheta, Sketchfab.'
      ],
      links: [
        {
          label: 'Houston Rockets Basketball Stadium',
          href: 'https://sketchfab.com/3d-models/houston-rockets-basketball-stadium-b341e223883c43b98d0671bed1dd9670'
        },
        {
          label: 'Basketball',
          href: 'https://sketchfab.com/3d-models/basketball-b7357866e35e4e1181e7488ae0577bdb'
        }
      ]
    },
    {
      title: 'Libraries and Tools',
      items: [
        'Svelte/SvelteKit, D3.js, Chart.js, Three.js, and Tailwind CSS for the interface, charts, and 3D rendering.'
      ],
      links: [
        { label: 'SvelteKit', href: 'https://svelte.dev/docs/kit' },
        { label: 'D3.js', href: 'https://d3js.org/' },
        { label: 'Chart.js', href: 'https://www.chartjs.org/' },
        { label: 'Three.js', href: 'https://threejs.org/' },
        { label: 'Tailwind CSS', href: 'https://tailwindcss.com/' }
      ]
    },
    {
      title: 'Assistance',
      items: [
        'Thank you to classmates in CSCI 5609 for feedback, testing, and discussion.',
        'Thank you to Professor Wang for project guidance.'
      ]
    }
  ];
</script>

<section class="order-20 mt-10 pb-4">
  <article class="panel overflow-hidden border border-amber-200/20 bg-slate-900/90">
    <div class="grid gap-3 border-b border-white/10 px-5 py-4 lg:grid-cols-[auto_minmax(0,1fr)] lg:items-end lg:px-6">
      <div>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-amber-200/90">Acknowledgements</p>
        <h2 class="mt-2 text-xl font-bold text-white sm:text-2xl">Credits and references</h2>
      </div>
      <p class="max-w-5xl text-xs leading-5 text-slate-300 lg:justify-self-end lg:text-right">
        Public basketball data, cited 3D assets, visualization libraries, and course feedback supported this project.
      </p>
    </div>

    <div class="grid gap-3 px-4 py-4 md:grid-cols-2 xl:grid-cols-5 lg:px-5">
      <section class="rounded-xl border border-white/10 bg-slate-950/70 p-3">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-slate-400">Team Members</p>
        <ul class="mt-3 space-y-1.5 text-xs text-slate-200">
          {#each teamMembers as member}
            <li class="flex items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full bg-amber-200"></span>
              <span>{member}</span>
            </li>
          {/each}
        </ul>
      </section>

      {#each creditGroups as group}
        <section class="rounded-xl border border-white/10 bg-slate-950/70 p-3">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-slate-400">{group.title}</p>
          <ul class="mt-3 space-y-2 text-xs leading-5 text-slate-300">
            {#each group.items as item}
              <li>{item}</li>
            {/each}
          </ul>

          {#if group.links?.length}
            <div class="mt-3 flex flex-wrap gap-1.5">
              {#each group.links as link}
                <a
                  href={link.href}
                  class="rounded-full border border-amber-200/20 bg-amber-200/10 px-2.5 py-1 text-[0.68rem] font-bold leading-none text-amber-100 transition hover:border-amber-200/40 hover:bg-amber-200/15"
                  target="_blank"
                  rel="noreferrer"
                >
                  {link.label}
                </a>
              {/each}
            </div>
          {/if}
        </section>
      {/each}
    </div>
  </article>
</section>
