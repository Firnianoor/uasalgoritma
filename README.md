# Proyek Analisis Tingkat Pengangguran Terbuka Berdasarkan Pendidikan di Jawa Barat

## 📚 Deskripsi Proyek
Proyek ini merupakan analisis mendalam mengenai kondisi pengangguran terbuka di Provinsi Jawa Barat dari tahun 2011 hingga 2023. Fokus utama adalah meneliti hubungan antara tingkat pendidikan terakhir para pencari kerja dengan angka pengangguran. Melalui visualisasi interaktif dan analisis statistik, proyek ini bertujuan untuk:
* Mengidentifikasi kelompok pendidikan yang paling rentan terhadap pengangguran.
* Memahami tren dan fluktuasi angka pengangguran berdasarkan jenjang pendidikan dari waktu ke waktu.
* Menganalisis korelasi antar jenjang pendidikan terkait pengangguran.
* Memprediksi tren pengangguran di masa depan menggunakan regresi linear sederhana.

Aplikasi ini dibangun menggunakan Streamlit.

## 🎯 Topik yang Dipilih
**Topik No. 5: Analisis Tingkat Pengangguran dan Ketenagakerjaan**. Sesuai instruksi tugas, analisis ini menitikberatkan pada hubungan antara pendidikan dan pengangguran, serta memanfaatkan teknik regresi dan korelasi untuk analisis statistik sederhana.

## 📊 Sumber Data
Data yang digunakan dalam proyek ini adalah:
* **Dataset:** "Jumlah Pengangguran Terbuka Berdasarkan Pendidikan di Jawa Barat"
* **Periode Data:** 2011 - 2023
* **Sumber Resmi:** Badan Pusat Statistik (BPS) melalui Open Data Jawa Barat Provinsi
* **Tautan:** [https://opendata.jabarprov.go.id/id/dataset/jumlah-pengangguran-terbuka-berdasarkan-pendidikan-di-jawa-barat](https://opendata.jabarprov.go.id/id/dataset/jumlah-pengangguran-terbuka-berdasarkan-pendidikan-di-jawa-barat)
* **Nama File Lokal:** `cobadata.xlsx`

## 🛠️ Tools dan Library yang Digunakan


* **`streamlit`**: Framework untuk membangun aplikasi web interaktif dan dashboard data.
* **`pandas`**: Library utama untuk manipulasi dan analisis data (misalnya, membaca file Excel, membersihkan data, membuat pivot table, grouping, melakukan agregasi).
* **`numpy`**: Digunakan untuk operasi numerik, khususnya dalam pengaturan plot.
* **`matplotlib`**: Library dasar untuk membuat visualisasi statis dan kustomisasi plot.
* **`seaborn`**: Membangun di atas Matplotlib untuk membuat visualisasi statistik yang lebih menarik dan informatif, seperti heatmap.
* **`scipy`**: Digunakan untuk analisis statistik, khususnya modul `linregress` untuk regresi linear sederhana.
* **`openpyxl`**: Dependensi yang diperlukan oleh Pandas untuk membaca file `.xlsx`.

## ⚙️ Struktur Proyek dan Alur Kerja Aplikasi

Proyek ini diimplementasikan dalam satu file utama, `app.py`, yang mengintegrasikan seluruh fungsionalitas dari pemuatan data hingga penyajian hasil interaktif. Berikut adalah struktur dan penjelasan detail setiap bagian dalam `app.py` yang menggambarkan alur kerja aplikasi:

### `app.py` - Detail Struktur Kode dan Alur Kerja

1.  **Konfigurasi Halaman (Streamlit Page Configuration)**
    * **Tujuan:** Mengatur properti dasar halaman aplikasi Streamlit untuk tampilan yang optimal.
    * **Detail:** Bagian awal kode ini menggunakan `st.set_page_config()` untuk menentukan judul halaman browser (`page_title`) dan layout halaman (`layout="wide"`) agar konten dapat ditampilkan lebih luas dan efisien.

2.  **Pemuatan & Pembersihan Data (Load & Cleaning Data)**
    * **Tujuan:** Membaca data mentah dari file Excel dan melakukan pra-pemrosesan yang diperlukan agar data siap dianalisis dan divisualisasikan.
    * **Detail:**
        * Fungsi `load_data()` didefinisikan untuk menampung seluruh logika pemuatan dan pembersihan data.
        * Penggunaan dekorator `@st.cache_data` pada fungsi ini sangat penting. Ini memastikan bahwa data hanya dimuat dan dibersihkan sekali saat aplikasi pertama kali dijalankan atau kode berubah, secara signifikan mempercepat kinerja aplikasi pada setiap interaksi pengguna selanjutnya.
        * Melakukan pembacaan file `cobadata.xlsx` menggunakan `pd.read_excel()`.
        * Mengimplementasikan penanganan kesalahan (`try-except`) untuk kasus `FileNotFoundError` (file tidak ditemukan) atau `Exception` umum lainnya saat memuat data, sehingga aplikasi lebih robust.
        * Melakukan validasi awal untuk memastikan kolom-kolom esensial (`tahun`, `pendidikan`, `jumlah_pengangguran_terbuka`) yang diperlukan untuk analisis ada dalam DataFrame.
        * **Pembersihan & Pemetaan Kategori Pendidikan:** Ini adalah langkah krusial. Kode mengimplementasikan `education_map` (sebuah dictionary) dan fungsi `clean_education()`. Fungsi ini diterapkan pada kolom `pendidikan` untuk mengelompokkan berbagai nomenklatur pendidikan yang mungkin ada di data mentah (misalnya, "TIDAK/BELUM PERNAH SEKOLAH", "DIPLOMA I/II/III", "SMA UMUM", "SMA KEJURUAN") menjadi kategori standar yang lebih bersih dan konsisten (`SD KE BAWAH`, `SD`, `SMP`, `SMA`, `DIPLOMA/UNIV`). Ini memastikan bahwa analisis dan visualisasi dilakukan pada kategori yang seragam dan mudah dipahami.
        * Mengisi nilai kosong (NaN) di kolom `pendidikan` dengan 'UNKNOWN' sebelum proses pembersihan untuk menghindari error.
        * Memastikan kolom `tahun` memiliki tipe data integer untuk penggunaan yang benar dalam filter dan plotting.

3.  **Ekplorasi Data & Filter Interaktif (Data Exploration & Filtering)**
    * **Tujuan:** Menyediakan antarmuka bagi pengguna untuk berinteraksi dengan data dan menyaringnya sesuai kebutuhan analisis mereka.
    * **Detail:**
        * Menampilkan judul utama aplikasi (`st.title()`) dan caption sumber data (`st.caption()`).
        * Menggunakan `st.sidebar.header()` untuk menginisialisasi bagian filter di sidebar Streamlit, menjaga antarmuka utama tetap bersih.
        * `st.sidebar.slider()` digunakan untuk memilih rentang tahun analisis secara dinamis, memungkinkan pengguna untuk fokus pada periode tertentu.
        * `st.sidebar.multiselect()` memungkinkan pengguna untuk memilih atau membatalkan pilihan tingkat pendidikan yang ingin disertakan dalam analisis, memberikan fleksibilitas tinggi.
        * Melakukan filtering `DataFrame` utama (`df`) menjadi `df_filtered` berdasarkan pilihan tahun dan pendidikan yang dibuat oleh pengguna di sidebar.

4.  **Tampilan Data Mentah (Raw Data Display)**
    * **Tujuan:** Memberikan opsi bagi pengguna untuk melihat subset data mentah yang sedang aktif (setelah difilter) secara opsional.
    * **Detail:** Menggunakan `st.expander` yang dapat dibuka/tutup untuk menampung tampilan `st.dataframe()`. Ini membantu menjaga antarmuka utama aplikasi tetap rapi sambil tetap memberikan akses ke detail data jika diperlukan. Pesan informatif ditampilkan jika tidak ada data yang difilter.

5.  **Statistik Deskriptif (Descriptive Statistics)**
    * **Tujuan:** Menyajikan ringkasan statistik dasar dari data pengangguran yang difilter per kategori pendidikan, memberikan gambaran awal tentang distribusi data.
    * **Detail:** Menggunakan metode `df_filtered.groupby().describe()` untuk menghasilkan statistik seperti rata-rata, standar deviasi, nilai minimum, nilai maksimum, kuartil, dan jumlah data. Dilengkapi dengan pesan peringatan (`st.warning`) atau sukses (`st.success`) mengenai keberadaan nilai yang hilang (NaN) di data.

6.  **Persiapan Data untuk Visualisasi (Data Preparation for Visualizations)**
    * **Tujuan:** Mentransformasi `df_filtered` ke dalam format pivot table (`pivot`) yang lebih sesuai untuk plotting multi-series dan analisis perbandingan antar kategori pendidikan dari waktu ke waktu.
    * **Detail:** Menggunakan `df_filtered.pivot_table()` dengan `tahun` sebagai indeks, `pendidikan_bersih` sebagai kolom baru, dan `jumlah_pengangguran_terbuka` sebagai nilai agregasi. Ini memudahkan pembuatan grafik tren dan perbandingan antar jenjang.

7.  **Visualisasi Data (Visualizations)**
    * **Tujuan:** Memvisualisasikan pola, tren, dan hubungan dalam data pengangguran melalui berbagai jenis grafik yang informatif.
    * **Detail:** Setiap visualisasi ditempatkan di bawah subheader terpisah (`st.subheader`) dan dibuat menggunakan Matplotlib atau Seaborn. Pentingnya, setiap bagian visualisasi dilengkapi dengan penanganan kondisi `if pivot.empty` atau `len(available_cols) == 0`. Ini memastikan aplikasi tidak crash jika tidak ada data yang cukup untuk plot, melainkan menampilkan pesan informatif kepada pengguna.
        * **Tren Pengangguran (Line Plot)**: Menampilkan bagaimana jumlah pengangguran berubah dari tahun ke tahun untuk setiap tingkat pendidikan yang dipilih.
        * **Proporsi Pengangguran (Stacked Bar Chart)**: Memvisualisasikan kontribusi persentase setiap jenjang pendidikan terhadap total pengangguran terbuka per tahun. **Fitur unggulan: Label persentase langsung pada bar** untuk memudahkan interpretasi visual dari proporsi setiap kategori.
        * **Heatmap Korelasi**: Menggunakan Seaborn (`sns.heatmap`) untuk menunjukkan matriks korelasi antara jumlah pengangguran di berbagai jenjang pendidikan, mengungkapkan hubungan linier antar kategori.
        * **Regresi Linear Sederhana**: Melakukan loop melalui setiap kategori pendidikan yang tersedia. Untuk setiap kategori, `scipy.stats.linregress` digunakan untuk menghitung persamaan garis regresi, koefisien determinasi (R-squared), dan mengidentifikasi arah tren (naik/turun/stabil) jumlah pengangguran terhadap tahun. Hasil ditampilkan menggunakan `st.info` dan `st.markdown`.
        * **Grouped Bar Chart**: Menggunakan Matplotlib untuk membandingkan jumlah pengangguran antar jenjang pendidikan secara langsung untuk setiap tahun yang difilter, memberikan perspektif perbandingan absolut.

8.  **Fitur Download Data & Visualisasi (Download Features)**
    * **Tujuan:** Memberikan kemampuan kepada pengguna untuk mengunduh data yang sedang difilter dan salah satu visualisasi kunci (grafik tren).
    * **Detail:** Menyediakan tombol `st.download_button` untuk mengunduh `df_filtered` sebagai file CSV dan grafik tren (yang disimpan di `fig1`) sebagai gambar PNG.

9.  **Interpretasi Hasil Analisis (Interpretation of Results)**
    * **Tujuan:** Memberikan penjelasan kontekstual dan wawasan yang mendalam dari setiap visualisasi dan analisis statistik yang ditampilkan.
    * **Detail:** Bagian ini ditulis dalam format Markdown (`st.markdown`), terstruktur dengan sub-heading untuk setiap visualisasi. Ini berfungsi sebagai dokumentasi naratif yang komprehensif dari temuan proyek. **Fitur UX: Link navigasi internal** (misalnya, `[Lanjut ke Interpretasi Tren](#interpretasi-hasil-visualisasi-tren)`) memungkinkan pengguna untuk melompat cepat ke bagian interpretasi yang relevan di halaman.

10. **Kesimpulan & Rekomendasi (Conclusion & Recommendations)**
    * **Tujuan:** Merangkum temuan utama dari seluruh analisis data dan mengusulkan rekomendasi kebijakan yang praktis berdasarkan wawasan yang diperoleh.
    * **Detail:** Bagian ini menyajikan rangkuman poin-poin penting yang ditemukan sepanjang analisis. Ini mengonfirmasi lingkup geografis (Jawa Barat) dan rentang waktu. Diakhiri dengan rekomendasi konkret yang dapat dipertimbangkan oleh pembuat kebijakan. Bagian ini juga menyertakan ringkasan dinamis "Pada filter saat ini" untuk menampilkan rata-rata pengangguran tertinggi dan tahun pengangguran tertinggi berdasarkan data yang sedang difilter, memberikan relevansi langsung.

---

