// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

declare module 'three/examples/jsm/controls/OrbitControls.js' {
	export const OrbitControls: any;
}

declare module 'three/examples/jsm/loaders/GLTFLoader.js' {
	export const GLTFLoader: any;
}

export {};
