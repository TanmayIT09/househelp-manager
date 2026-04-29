package com.example.househelp

import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private val localServerIp by lazy { getString(R.string.local_server_ip) }
    private val backendUrls by lazy {
        listOf(
            if (isEmulator()) "http://10.0.2.2:5000" else "http://127.0.0.1:5000",
            "http://10.0.2.2:5000",
            "http://127.0.0.1:5000",
            "http://$localServerIp:5000"
        ).distinct()
    }
    private var currentUrlIndex = 0

    private fun isEmulator(): Boolean {
        return Build.FINGERPRINT.startsWith("generic") ||
            Build.FINGERPRINT.startsWith("unknown") ||
            Build.MODEL.contains("google_sdk") ||
            Build.MODEL.contains("Emulator") ||
            Build.MODEL.contains("Android SDK built for x86") ||
            Build.MANUFACTURER.contains("Genymotion") ||
            Build.HARDWARE.contains("goldfish") ||
            Build.HARDWARE.contains("ranchu") ||
            Build.HARDWARE.contains("qemu")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val webView = findViewById<WebView>(R.id.webView)
        val loadingBar = findViewById<ProgressBar>(R.id.loadingBar)
        val errorText = findViewById<TextView>(R.id.errorText)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                view.loadUrl(request.url.toString())
                return true
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                super.onPageStarted(view, url, favicon)
                loadingBar.visibility = View.VISIBLE
                errorText.visibility = View.GONE
                android.util.Log.d("HouseHelp", "Loading: $url")
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                loadingBar.visibility = View.GONE
                android.util.Log.d("HouseHelp", "Page loaded: $url")
            }

            override fun onReceivedError(view: WebView?, request: android.webkit.WebResourceRequest?, error: android.webkit.WebResourceError?) {
                super.onReceivedError(view, request, error)
                if (request?.isForMainFrame == true && currentUrlIndex < backendUrls.size - 1) {
                    currentUrlIndex += 1
                    val nextUrl = backendUrls[currentUrlIndex]
                    android.util.Log.w("HouseHelp", "Primary URL failed, trying fallback: $nextUrl")
                    view?.loadUrl(nextUrl)
                    return
                }

                loadingBar.visibility = View.GONE
                errorText.visibility = View.VISIBLE
                errorText.text = "Error loading page. Try adb reverse tcp:5000 tcp:5000 or set your PC IP in strings.xml."
                android.util.Log.e("HouseHelp", "Error: ${error?.description}")
            }
        }

        val startUrl = backendUrls[currentUrlIndex]
        webView.loadUrl(startUrl)
        android.util.Log.d("HouseHelp", "Starting to load: $startUrl")
    }
}
