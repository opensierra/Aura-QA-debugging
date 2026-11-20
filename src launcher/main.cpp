#include <windows.h>
#include <mmsystem.h>
#include <gdiplus.h>
#include <cmath>
#include <filesystem>
#include <string>

using namespace Gdiplus;

namespace fs = std::filesystem;

static void report(const std::string& title, const std::string& msg, UINT icon) {
    MessageBoxA(NULL, msg.c_str(), title.c_str(), MB_OK | icon);
}

// --- Splash nativo Win32 (sin WebView, sin dependencias) ---
static HWND     g_splash = NULL;
static Bitmap*  g_logo = NULL;
static int      g_W = 312, g_H = 210;
static double   g_pos = 0;             // posicion del segmento de carga (0..100)
static bool     g_anim = true;

static void drawSplash() {
    if (!g_splash) return;
    PAINTSTRUCT ps;
    HDC hdc = BeginPaint(g_splash, &ps);
    RECT rc; GetClientRect(g_splash, &rc);
    int W = rc.right - rc.left, H = rc.bottom - rc.top;
    // Doble buffer: dibujar en memoria y copiar de una vez (sin parpadeo).
    HDC mem = CreateCompatibleDC(hdc);
    HBITMAP bmp = CreateCompatibleBitmap(hdc, W, H);
    HBITMAP old = (HBITMAP)SelectObject(mem, bmp);
    // Fondo
    HBRUSH bg = CreateSolidBrush(RGB(29, 29, 29));
    FillRect(mem, &rc, bg);
    DeleteObject(bg);

    Graphics g(mem);
    g.SetSmoothingMode(SmoothingModeAntiAlias);
    g.SetTextRenderingHint(TextRenderingHintClearTypeGridFit);

    // Logo (centrado, arriba).
    if (g_logo) {
        const int lh = 62;
        const int lw = (int)(g_logo->GetWidth() * (float)lh / g_logo->GetHeight());
        g.DrawImage(g_logo, (W - lw) / 2, 16, lw, lh);
    }

    // Titulo.
    {
        FontFamily ff(L"Segoe UI");
        Font font(&ff, 19, FontStyleBold, UnitPixel);
        SolidBrush brush(Color(255, 228, 228, 228));
        StringFormat sf;
        sf.SetAlignment(StringAlignmentCenter);
        g.DrawString(L"AURA QA", -1, &font,
                     RectF(0, 86, W, 28), &sf, &brush);
    }
    // Tagline (del About).
    {
        FontFamily ff(L"Segoe UI");
        Font font(&ff, 11, FontStyleRegular, UnitPixel);
        SolidBrush brush(Color(255, 136, 136, 136));
        StringFormat sf;
        sf.SetAlignment(StringAlignmentCenter);
        g.DrawString(L"Automated QA for Android apps", -1, &font,
                     RectF(0, 116, W, 18), &sf, &brush);
    }

    // Geometria de la barra (pista redondeada, delgada, centrada).
    const int barW = 180, barH = 3;
    const int bx = (W - barW) / 2;
    const int by = 152;

    // Pista: rectangulo redondeado gris oscuro.
    {
        GraphicsPath path;
        path.AddArc(bx, by, barH, barH, 90, 180);
        path.AddArc(bx + barW - barH, by, barH, barH, 270, 180);
        path.CloseFigure();
        SolidBrush track(Color(255, 58, 58, 58));
        g.FillPath(&track, &path);
    }

    // Segmento "cometa": cola difuminada -> cabeza brillante, desplazandose.
    if (g_anim) {
        const int seg = barW / 3;
        int x = bx + (int)(g_pos / 100.0 * (barW - seg));
        // Recorta al area de la pista para que el segmento no se salga.
        GraphicsPath clip;
        clip.AddArc(bx, by, barH, barH, 90, 180);
        clip.AddArc(bx + barW - barH, by, barH, barH, 270, 180);
        clip.CloseFigure();
        g.SetClip(&clip);

        // Fade global: el segmento aparece suavemente al entrar por la
        // izquierda y desaparece al salir por la derecha (evita el corte
        // abrupto en los bordes de la pista).
        float fade = 1.0f;
        if (g_pos < 20) fade = (float)g_pos / 20.0f;
        else if (g_pos > 80) fade = (float)(100.0 - g_pos) / 20.0f;

        // Degradado manual de cometa: alpha 0 (cola) -> 255 (cabeza), y el
        // color pasa de azul a azul-blanco en la punta.
        const int N = 40;
        for (int i = 0; i < N; i++) {
            float t = (float)i / (N - 1);          // 0 = cola, 1 = cabeza
            int a = (int)(255.0f * t * t * fade);  // rampa suave (cuadratica)
            int r = (int)(59  + (150 - 59)  * t);
            int gg = (int)(130 + (200 - 130) * t);
            int b = (int)(246 + (255 - 246) * t);
            int x0 = x + (int)(t * seg);
            int x1 = x + (int)((i + 1) * (float)seg / N);
            if (x1 <= x0) x1 = x0 + 1;
            SolidBrush brush(Color(a, r, gg, b));
            g.FillRectangle(&brush, x0, by, x1 - x0, barH);
        }
        g.ResetClip();
    }

    // Version (pie).
    {
        FontFamily ff(L"Segoe UI");
        Font font(&ff, 9, FontStyleRegular, UnitPixel);
        SolidBrush brush(Color(255, 96, 96, 96));
        StringFormat sf;
        sf.SetAlignment(StringAlignmentCenter);
        g.DrawString(L"(Debugging) Beta-0.1", -1, &font,
                     RectF(0, 176, W, 16), &sf, &brush);
    }

    BitBlt(hdc, 0, 0, W, H, mem, 0, 0, SRCCOPY);
    SelectObject(mem, old);
    DeleteObject(bmp);
    DeleteDC(mem);
    EndPaint(g_splash, &ps);
}

static LRESULT CALLBACK SplashProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {
    case WM_ERASEBKGND:
        // No borrar: el doble buffer pinta el fondo completo (evita parpadeo).
        return 1;
    case WM_TIMER:
        if (g_anim) {
            g_pos += 0.5;
            if (g_pos > 100) g_pos = 0;
            InvalidateRect(hwnd, NULL, FALSE);
        }
        return 0;
    case WM_PAINT:
        drawSplash();
        return 0;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcA(hwnd, msg, wp, lp);
}

static void createSplash(const std::string& baseDir) {
    WNDCLASSA wc = {0};
    wc.lpfnWndProc   = SplashProc;
    wc.hInstance     = GetModuleHandleA(NULL);
    wc.lpszClassName = "AuraSplash";
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    RegisterClassA(&wc);
    int sx = (GetSystemMetrics(SM_CXSCREEN) - g_W) / 2;
    int sy = (GetSystemMetrics(SM_CYSCREEN) - g_H) / 2;
    g_splash = CreateWindowExA(WS_EX_TOPMOST, "AuraSplash", "AURA QA",
        WS_POPUP, sx, sy, g_W, g_H, NULL, NULL, GetModuleHandleA(NULL), NULL);
    // Logo (PNG transparente, pre-renderizado desde aura_logo.svg).
    std::string logoPath = baseDir + "\\UI\\vendor\\aura_logo_splash.png";
    if (fs::exists(logoPath)) {
        std::wstring w(logoPath.begin(), logoPath.end());
        g_logo = new Bitmap(w.c_str());
        if (g_logo->GetLastStatus() != Ok) { delete g_logo; g_logo = NULL; }
    }
    ShowWindow(g_splash, SW_SHOW);
    UpdateWindow(g_splash);
    SetTimer(g_splash, 1, 13, NULL);
}

static void destroySplash() {
    if (g_splash) {
        g_anim = false;
        KillTimer(g_splash, 1);
        DestroyWindow(g_splash);
        g_splash = NULL;
    }
    if (g_logo) { delete g_logo; g_logo = NULL; }
}

static std::string signalPath(DWORD pid) {
    char tmp[MAX_PATH];
    GetTempPathA(MAX_PATH, tmp);
    return std::string(tmp) + "aura_ready_" + std::to_string(pid) + ".txt";
}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
    // Sube la resolucion del reloj del sistema a 1 ms para que el timer de
    // la animacion corra a ~77 fps (el timer de Win32 por defecto se
    // cuantiza a ~15.6 ms).
    timeBeginPeriod(1);

    // Inicializa GDI+ (para el degradado suave de la barra de carga).
    ULONG_PTR gdiplusToken = 0;
    GdiplusStartupInput gdiplusInput;
    GdiplusStartup(&gdiplusToken, &gdiplusInput, NULL);

    // 1. Resuelve su propia ubicacion (raiz del proyecto, junto a Python\ y GUI).
    wchar_t buf[MAX_PATH];
    if (GetModuleFileNameW(NULL, buf, MAX_PATH) == 0) {
        report("launcher.exe", "No se pudo obtener la ruta del ejecutable.", MB_ICONERROR);
        GdiplusShutdown(gdiplusToken);
        timeEndPeriod(1);
        return 1;
    }
    fs::path dir = fs::path(buf).parent_path();
    fs::path python = dir / "Python" / "python.exe";
    fs::path script  = dir / "GUI";

    // 2. Valida que existan los archivos necesarios.
    if (!fs::exists(python)) {
        report("launcher.exe - Faltan archivos", "No se encontro:\n" + python.string(), MB_ICONERROR);
        GdiplusShutdown(gdiplusToken);
        timeEndPeriod(1);
        return 1;
    }
    if (!fs::exists(script)) {
        report("launcher.exe - Faltan archivos", "No se encontro:\n" + script.string(), MB_ICONERROR);
        GdiplusShutdown(gdiplusToken);
        timeEndPeriod(1);
        return 1;
    }

    // 3. Splash nativo: visible en ~0 ms, antes de que Python arranque.
    createSplash(dir.string());

    // 4. Job Object: al cerrar el launcher, Windows mata python Y TODO su arbol.
    HANDLE job = CreateJobObjectA(NULL, NULL);
    if (job) {
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION li = {0};
        li.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        SetInformationJobObject(job, JobObjectExtendedLimitInformation, &li, sizeof(li));
    }

    // 5. Linea de comando.
    std::string cmd = "\"" + python.string() + "\" \"" + script.string() + "\"";
    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);
    if (!CreateProcessA(NULL, (LPSTR)cmd.c_str(), NULL, NULL, FALSE,
                        CREATE_NO_WINDOW | CREATE_SUSPENDED, NULL,
                        dir.string().c_str(), &si, &pi)) {
        DWORD err = GetLastError();
        report("launcher.exe - Error",
               "No se pudo iniciar python.exe.\nCodigo de error: " + std::to_string(err),
               MB_ICONERROR);
        if (job) CloseHandle(job);
        destroySplash();
        GdiplusShutdown(gdiplusToken);
        timeEndPeriod(1);
        return 1;
    }

    // 6. Asigna el hijo al job y lo reanuda.
    if (job) {
        AssignProcessToJobObject(job, pi.hProcess);
        ResumeThread(pi.hThread);
    }

    // 7. Polling: espera senal de ready O fin del proceso O timeout 60s.
    //    Usa MsgWaitForMultipleObjects para que el bucle de mensajes (y el
    //    timer de la animacion) siga corriendo a plena velocidad.
    //    Cuando la senal llega, el splash se mantiene 3 segundos mas.
    std::string sig = signalPath(pi.dwProcessId);
    DWORD start = GetTickCount();
    DWORD sigTime = 0;
    while (true) {
        DWORD wr = MsgWaitForMultipleObjects(1, &pi.hProcess, FALSE, 13, QS_ALLINPUT);
        if (wr == WAIT_OBJECT_0) break;               // python termino
        if (wr == WAIT_OBJECT_0 + 1) {                // hay mensajes
            MSG msg;
            while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
                TranslateMessage(&msg);
                DispatchMessageA(&msg);
            }
        }
        if (fs::exists(sig)) {
            if (!sigTime) sigTime = GetTickCount();
            if (GetTickCount() - sigTime >= 3000) break;
        }
        if (GetTickCount() - start > 60000) break;
    }

    // 8. Cierra splash y avisa a python que ya puede mostrar la ventana.
    destroySplash();
    {
        char tmp[MAX_PATH];
        GetTempPathA(MAX_PATH, tmp);
        std::string show = std::string(tmp) + "aura_show_" + std::to_string(pi.dwProcessId) + ".txt";
        FILE* f = fopen(show.c_str(), "w");
        if (f) { fputs("1", f); fclose(f); }
    }
    fs::remove(sig);

    // 9. Espera a que el usuario cierre la app (python termina).
    WaitForSingleObject(pi.hProcess, INFINITE);

    // 10. Cierra handles.
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    if (job) CloseHandle(job);
    GdiplusShutdown(gdiplusToken);
    timeEndPeriod(1);
    return 0;
}
