from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
# [Pastikan import logging ada di awal file]

# Konfigurasi dasar: Semua log level INFO ke atas akan ditampilkan
# Format: Waktu - Level Nama Kelas/Fungsi - Pesan
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
# Tambahkan logger untuk kelas yang akan kita gunakan
LOGGER = logging.getLogger('Checkout')

# Tambahan logger untuk kelas notifikasi dan metode pembayaran
LOGGER2 = logging.getLogger('Notifikasi')
LOGGER3 = logging.getLogger('Metode Pembayaran')

# Model sederhana
@dataclass
class Order:
    """
    Kelas untuk menyimpan data string(customer_name dan status = open)
    dan float(total_price)
    """
    customer_name: str
    total_price: float
    status: str = "open"

# --- ABSTRAKSI (Kontrak untuk OCP/DIP) ---
class IPaymentProcessor(ABC):
    """
    Interface/antarmuka/kontrak untuk seluruh metode pembayaran
    Kontrak: Semua Prosesor pembayaran harus punya method 'process'.
    
    Kelas ini mendefinisikan method abstrak 'process' yang harus
    diimplementasikan pada setiap kelas turunan dengan menambahkan kelas metode pembayaran baru.
    Aturan: Tidak boleh diinstansi langsung pada kelas abstrak
    """
    @abstractmethod
    def process(self, order: Order):
        """
        Memproses pembayaran untuk sebuah proses pesanan.

        Args:
            order (Order): Objek pesanan yang berisi informasi proses transaksi.
        """
        pass

class INotificationService(ABC):
    """
    Interface/antarmuka/kontrak untuk seluruh model notifikas
    Kontrak: Semua layanan notifikasi harus punya method 'send'.
    
    Kelas ini mendefinisikan pada method abstrak 'send' yang harus
    diimplementasikan pada setiap kelas turunan dengan menambahkan kelas model notifikasi baru.
    Aturan: Tidak boleh diinstansi langung pada kelas abstrak
    """
    @abstractmethod
    def send(self, order: Order):
        """
        Mengirimkan notifikasi berdasarkan informasi pesanan order

        Args:
            order (Order): Objek pesanan yang berisi informasi data
                           transaksi, nama pelanggan, total harga dan status pesanan.
                           Objek ini digunakan untuk menentukan isi model notifikasi
        """
        pass
    
# --- IMPLEMENTASI KONKRIT (Plug-In) ---
class CreditCardProcessor(IPaymentProcessor):
    """
    Implementasi detail konkret dari kelas IPaymentProcessor untuk proses pembayaran
    menggunakan kartu kredit
    
    Kelas ini mengimplementasikan pada kontrak 'process' pada definisi dalam kelas induk(IPaymentProcessor),
    ini dapat digunakan pada proses pembayaran(plug-in) di kelas high level(CheckoutService)
    tanpa mengubah/modifikasi pada kelas high-level(CheckoutService) (memenuhi DIP/OCP)
    """
    def process(self, order: Order) -> bool:
        """
        Menjalankan proses pembayaran dengan metode pembayaran kartu kredit

        Args:
            order (Order): Objek pesanan yang berisi informasi transaksi metode pembayaran
            yang akan diproses

        Returns:
            bool: True jika pembayaran dengan metode ini berhasil, False jika gagal
        """
        LOGGER3.info("Payment: Memproses Kartu Kredit.")
        return True

class EmailNotifier(INotificationService):
    """
    Implementasi detail konkret dari kelas INotificationService untuk proses notifikasi
    menggunakan notfikasi email

    Kelas ini mengimplementasikan pada kontrak 'send' yang didefinisikan dalam kelas induk (INotificationService),
    ini dapat digunakan pada proses notifikasi(plug-in) di kelas high-level(CheckoutService)
    tanpa mengubah/modifikasi pada kelas high-level(CheckoutService) (memenuhi DIP/OCP)
    """
    def send(self, order:Order):
        """
        Menjalankan proses notifikasi dengan model notifikasi email

        Args:
            order (Order): Objek pesanan yang berisi informasi pemberitahuan(notifikasi)
            model email yang akan diproses
        """
        LOGGER2.info(f"Notif: Mengirim email konfirmasi ke {order.customer_name}.")

# --- KELAS KOORDINATOR (SRP & DIP) ---
class CheckoutService: # Tanggung Jawab Tunggal: Mengkoordinasi Checkout
    """
    Kelas High - Level untuk mengkoordinasi proses transaksi pembayaran.
    
    Kelas ini memisahkan logika pembayaran dan notifikasi (memenuhi SRP)
    """
    def __init__(self, payment_processor: IPaymentProcessor, notifier: INotificationService):
        """
        Menginisialisasi ChechkoutService dengan depedensi yang diperlukan.

        Args:
            payment_processor (IPaymentProcessor): Implementasi interface pembayaran.
            notifier (INotificationService): Implementasi interface notifikasi.
        """
        # Depedency Injection (DIP): Bergantung pada Abstraksi, bukan konkrit
        self.payment_processor = payment_processor
        self.notifier = notifier
    
    def run_checkout(self, order: Order):
        """
        Menjalankan proses checkout dan memvalidasi pembayaran.

        Args:
            order (Order): Objek pesanan yang akan diproses.

        Returns:
            bool: True jika checkout sukses, False jika gagal
        """
        # Logging alih - alih print()
        LOGGER.info(f"Memulai checkout untuk {order.customer_name}. Total: {order.total_price}")
        payment_success = self.payment_processor.process(order) # Delegasi 1
        
        if payment_success:
            order.status = "paid"
            self.notifier.send(order) # Delegasi 2
            LOGGER.info("Checkout Sukses. Status pesanan: PAID")
            return True
        else:
            # Gunakan level ERROR/WARNING untuk masalah
            LOGGER.error("Pembayaran gagal. Transaksi dibatalkan.")
            return False

# --- PROGRAM UTAMA ---
# Setup Depedencies
andi_order = Order("Andi", 500000)
email_service = EmailNotifier()

# 1. Inject implementasi Credit Card
cc_processor = CreditCardProcessor()
checkout_cc = CheckoutService(payment_processor = cc_processor, notifier = email_service)
print("--- Skenario 1: Credit Card ---")
checkout_cc.run_checkout(andi_order)

# 2. Pembuktian OCP: Menambah Metode Pembayaran QRIS (Tanpa Mengubah CheckoutService)
class QrisProcessor(IPaymentProcessor):
    """
    Implementasi detail konkret dari kelas IPaymentProcessor untuk proses pembayaran
    menggunakan Qris
    
    Kelas ini mengimplementasikan pada kontrak 'process' pada definisi dalam kelas induk(IPaymentProcessor),
    ini dapat digunakan pada proses pembayaran(plug-in) di kelas high level(CheckoutService)
    tanpa mengubah/modifikasi pada kelas high-level(CheckoutService) (memenuhi DIP/OCP)
    """
    def process(self, order: Order) -> bool:
        """
        Args:
            order (Order): Objek pesanan yang berisi informasi transaksi metode pembayaran
            yang akan diproses

        Returns:
            bool: True jika pembayaran dengan metode ini berhasil, False jika gagal
        """
        LOGGER3.info("Payment: Memproses QRIS.")
        return True
    
budi_order = Order("Budi", 100000)
qris_processor = QrisProcessor()

# Inject implementasi QRIS yang baru dimuat
checkout_qris = CheckoutService(payment_processor = qris_processor, notifier = email_service)
print("\n--- Skenario 2: Pembuktian OCP (QRIS) ---")
checkout_qris.run_checkout(budi_order)