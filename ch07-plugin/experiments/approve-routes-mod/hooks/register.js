export function register(on) {
  on('tool.check', { tool: 'Bash' }, async ($, e, next) => {
    const decided = await next(e)
    if (e.input.command === 'node scripts/check-routes.js') {
      return { decision: 'allow' }
    }
    return decided
  })
}
