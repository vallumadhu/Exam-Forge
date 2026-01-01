import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { spawn } from 'child_process'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

let pyProc = null

function startBackend() {
  const isDev = is.dev

  if (isDev) {
    console.log('Starting backend in DEVELOPMENT mode')

    const backendPath = join(__dirname, '../../../backend')

    const activateCmd = process.platform === 'win32'
      ? `venv\\Scripts\\activate && python main.py --host 127.0.0.1 --port 6871`
      : `source venv/bin/activate && python main.py --host 127.0.0.1 --port 6871`

    pyProc = spawn(activateCmd, [], {
      cwd: backendPath,
      stdio: 'inherit',
      shell: true
    })
  } else {

    console.log('Starting backend in PRODUCTION mode')

    const exeName = process.platform === 'win32' ? 'main.exe' : 'main'
    const exePath = join(process.resourcesPath, 'backend', exeName)

    console.log('Backend executable path:', exePath)

    pyProc = spawn(exePath, [
      '--host', '127.0.0.1',
      '--port', '6871'
    ], {
      stdio: 'inherit'
    })
  }

  console.log('Backend starting on http://127.0.0.1:6871')

  pyProc.on('error', (err) => {
    console.error('Failed to start backend:', err)
  })

  pyProc.on('exit', (code) => {
    console.log(`Backend process exited with code ${code}`)
  })
}

function stopBackend() {
  if (pyProc) {
    pyProc.kill()
    pyProc = null
    console.log('Backend stopped')
  }
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1100,
    height: 700,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  startBackend()

  electronApp.setAppUserModelId('com.electron')

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('quit', stopBackend)
app.on('will-quit', stopBackend)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
