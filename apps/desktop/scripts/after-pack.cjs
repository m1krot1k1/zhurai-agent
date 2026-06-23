/**
 * after-pack.cjs — electron-builder afterPack hook.
 *
 * Windows: stamp Hermes/ZhurAI exe identity via rcedit.
 * macOS: ad-hoc codesign when no Developer ID (CSC_LINK / APPLE_SIGNING_IDENTITY).
 */

const fs = require('node:fs')
const path = require('node:path')
const { execFile } = require('node:child_process')
const { promisify } = require('node:util')

const { stampExeIdentity } = require('./set-exe-identity.cjs')

const execFileAsync = promisify(execFile)

async function adhocSignMacApp(appPath) {
  if (!fs.existsSync(appPath)) {
    return
  }
  const link = process.env.CSC_LINK
  const pw = process.env.CSC_KEY_PASSWORD
  const hasDevSigning =
    Boolean(process.env.APPLE_SIGNING_IDENTITY) ||
    (Boolean(link && pw) && (link.includes('BEGIN') || fs.existsSync(link)))
  if (hasDevSigning) {
    return
  }
  try {
    await execFileAsync('xattr', ['-cr', appPath]).catch(() => {})
    await execFileAsync('codesign', ['--force', '--deep', '--sign', '-', appPath])
    console.log(`[after-pack] ad-hoc signed ${appPath}`)
  } catch (err) {
    console.warn(`[after-pack] macOS ad-hoc sign failed (${err.message})`)
  }
}

exports.default = async function afterPack(context) {
  const productName = context.packager?.appInfo?.productFilename || 'ZhurAI Agent'

  if (context.electronPlatformName === 'darwin') {
    const appPath = path.join(context.appOutDir, `${productName}.app`)
    await adhocSignMacApp(appPath)
    return
  }

  if (context.electronPlatformName !== 'win32') {
    return
  }

  const exe = path.join(context.appOutDir, `${productName}.exe`)
  const desktopRoot = path.resolve(__dirname, '..')

  try {
    await stampExeIdentity(exe, desktopRoot)
  } catch (err) {
    console.warn(
      `[after-pack] exe identity stamp failed (${err.message}); exe keeps the stock Electron icon`
    )
  }
}
