// ... (código existente) ...

class MainActivity : AppCompatActivity() {
    private lateinit var statusTextView: TextView
    private lateinit var connectButton: Button
    private lateinit var lockButton: Button
    private lateinit var unlockButton: Button  // Nuevo botón
    private lateinit var tokenEditText: EditText
    private var isConnected = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusTextView = findViewById(R.id.statusTextView)
        connectButton = findViewById(R.id.connectButton)
        lockButton = findViewById(R.id.lockButton)
        unlockButton = findViewById(R.id.unlockButton)  // Nuevo botón
        tokenEditText = findViewById(R.id.tokenEditText)

        connectButton.setOnClickListener { connectToPC() }
        lockButton.setOnClickListener { lockPC() }
        unlockButton.setOnClickListener { unlockPC() }  // Nuevo listener
    }

    // ... (código existente) ...

    private fun unlockPC() {
        if (!isConnected) {
            statusTextView.text = "No conectado a la PC"
            return
        }

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val factory = SSLSocketFactory.getDefault() as SSLSocketFactory
                val socket = factory.createSocket("201.254.118.87", 12345) as SSLSocket
                
                val writer = PrintWriter(socket.outputStream, true)
                val reader = BufferedReader(socket.inputStream.reader())

                // Autenticación
                writer.println(tokenEditText.text.toString())
                if (reader.readLine() != "Autenticado") {
                    withContext(Dispatchers.Main) {
                        statusTextView.text = "Autenticación fallida"
                    }
                    return@launch
                }

                writer.println("UNLOCK")
                val response = reader.readLine()
                withContext(Dispatchers.Main) {
                    statusTextView.text = response
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    statusTextView.text = "Error al enviar comando: ${e.message}"
                }
            }
        }
    }
}