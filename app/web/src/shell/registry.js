const _modules = [];

export function register(module) {
  if (!_modules.find((m) => m.id === module.id)) _modules.push(module);
}

export function getModules() {
  return _modules.slice();
}
