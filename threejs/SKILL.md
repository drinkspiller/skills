---
name: threejs
description: >
  Three.js 3D graphics development covering fundamentals, geometry, materials,
  lighting, textures, animation, loaders, shaders, interaction, and
  postprocessing. Use when building 3D web experiences, creating WebGL content,
  working with Three.js scenes, or needing help with 3D rendering concepts.
---

# Three.js Skills

A comprehensive guide to Three.js 3D graphics development. Covers the full
spectrum from scene setup to advanced postprocessing.

## Fundamentals

### Scene Setup

```javascript
import * as THREE from "three";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();
```

### Cameras

-   **PerspectiveCamera(fov, aspect, near, far)** — realistic perspective
-   **OrthographicCamera(left, right, top, bottom, near, far)** — no perspective
    distortion, good for 2D/isometric

### Object3D Hierarchy

All scene objects inherit from Object3D. Key properties: - `position` (Vector3),
`rotation` (Euler), `scale` (Vector3) - `add(child)`, `remove(child)` —
parent-child transforms - `traverse(callback)` — walk the subtree

## Geometry

### Built-in Geometries

```javascript
new THREE.BoxGeometry(width, height, depth);
new THREE.SphereGeometry(radius, widthSegments, heightSegments);
new THREE.PlaneGeometry(width, height);
new THREE.CylinderGeometry(radiusTop, radiusBottom, height);
new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments);
```

### BufferGeometry (Custom)

```javascript
const geometry = new THREE.BufferGeometry();
const vertices = new Float32Array([...]);
geometry.setAttribute("position",
  new THREE.BufferAttribute(vertices, 3));
geometry.computeVertexNormals();
```

### InstancedMesh (Performance)

```javascript
const mesh = new THREE.InstancedMesh(geometry, material, count);
const matrix = new THREE.Matrix4();
for (let i = 0; i < count; i++) {
  matrix.setPosition(x, y, z);
  mesh.setMatrixAt(i, matrix);
}
mesh.instanceMatrix.needsUpdate = true;
```

## Materials

### Standard PBR

```javascript
new THREE.MeshStandardMaterial({
  color: 0xff0000,
  roughness: 0.5,
  metalness: 0.5,
  map: texture,          // albedo
  normalMap: normalTex,  // surface detail
  envMap: envTexture,    // reflections
});
```

### Material Types (simple → complex)

-   **MeshBasicMaterial** — unlit, fastest
-   **MeshPhongMaterial** — Blinn-Phong shading
-   **MeshStandardMaterial** — PBR (recommended default)
-   **MeshPhysicalMaterial** — PBR + clearcoat, transmission, sheen
-   **ShaderMaterial** — custom GLSL

## Lighting

### Light Types

```javascript
new THREE.AmbientLight(0x404040);             // uniform fill
new THREE.DirectionalLight(0xffffff, 1);      // sun-like, parallel rays
new THREE.PointLight(0xffffff, 1, 100);       // omnidirectional
new THREE.SpotLight(0xffffff, 1, 100, angle); // cone
new THREE.HemisphereLight(sky, ground, 1);    // sky+ground
```

### Shadows

```javascript
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
light.castShadow = true;
light.shadow.mapSize.set(2048, 2048);
mesh.castShadow = true;
ground.receiveShadow = true;
```

## Textures

### Loading

```javascript
const loader = new THREE.TextureLoader();
const texture = loader.load("texture.jpg");
texture.colorSpace = THREE.SRGBColorSpace; // for color textures
texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
texture.repeat.set(2, 2);
```

### Environment Maps

```javascript
import { RGBELoader } from "three/addons/loaders/RGBELoader.js";
new RGBELoader().load("env.hdr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
  scene.background = texture;
});
```

## Animation

### AnimationMixer (GLTF animations)

```javascript
const mixer = new THREE.AnimationMixer(model);
const action = mixer.clipAction(clip);
action.play();

// In render loop:
mixer.update(delta);
```

### Procedural Animation

```javascript
const clock = new THREE.Clock();
function animate() {
  const elapsed = clock.getElapsedTime();
  mesh.position.y = Math.sin(elapsed) * 0.5;
  mesh.rotation.y += 0.01;
}
```

## Loaders

### GLTF/GLB (Recommended 3D format)

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath("/draco/");
const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

gltfLoader.load("model.glb", (gltf) => {
  scene.add(gltf.scene);
  // gltf.animations — AnimationClip[]
});
```

## Shaders

### ShaderMaterial

```javascript
new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0xff0000) },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(vUv, sin(uTime) * 0.5 + 0.5, 1.0);
    }
  `,
});
```

## Interaction

### Raycasting

```javascript
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

window.addEventListener("click", (event) => {
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const intersects = raycaster.intersectObjects(scene.children);
  if (intersects.length > 0) {
    const hit = intersects[0];
    // hit.object, hit.point, hit.face, hit.distance
  }
});
```

### OrbitControls

```javascript
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
// In render loop: controls.update();
```

## Postprocessing

### EffectComposer

```javascript
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(
  new THREE.Vector2(width, height), 1.5, 0.4, 0.85
));

// Replace renderer.render() with:
composer.render();
```

## Performance Tips

-   Use `InstancedMesh` for many identical objects
-   Merge static geometries with `BufferGeometryUtils.mergeGeometries()`
-   Limit shadow-casting lights and shadow map resolution
-   Dispose textures, geometries, and materials when removing objects
-   Use `renderer.info` to monitor draw calls and triangles
-   Set `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`
