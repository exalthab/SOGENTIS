// globe.js — Module pour l’animation du globe interactif avec Three.js

export function initGlobe(THREE) {
  const canvas = document.getElementById('globe-canvas');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  // Lumière
  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(2, 2, 5);
  scene.add(light);

  // Sphère (globe)
  const geometry = new THREE.SphereGeometry(1, 64, 64);
  const textureLoader = new THREE.TextureLoader();
  const texture = textureLoader.load('/static/core/textures/earth.jpg'); // Assure-toi d’avoir cette image
  const material = new THREE.MeshStandardMaterial({ map: texture });
  const globe = new THREE.Mesh(geometry, material);
  scene.add(globe);

  camera.position.z = 2.5;

  // Animation
  function animate() {
    requestAnimationFrame(animate);
    globe.rotation.y += 0.0025;
    renderer.render(scene, camera);
  }

  animate();

  // Resize dynamique
  window.addEventListener('resize', () => {
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  });
}
