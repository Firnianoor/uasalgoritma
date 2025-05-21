import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from scipy.stats import linregress

# Konfigurasi tampilan halaman Streamlit
st.set_page_config(page_title="Analisis Pengangguran Jawa Barat", layout="wide")

# =========================
# 1. LOAD & CLEANING DATA
# =========================

from typing import Any

# Fungsi untuk load dan cleaning data, hasilnya di-cache supaya efisien
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load and clean the unemployment data from CSV.
    Returns a DataFrame with an additional 'pendidikan_bersih' column.
    """
    try:
          # Membaca file Excel
        df = pd.read_excel('cobadata.xlsx')
    except Exception as e:
        # Jika gagal, tampilkan error dan return DataFrame kosong
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  

    # Cek apakah kolom 'pendidikan' ada
    if 'pendidikan' not in df.columns:
        st.error("Kolom 'pendidikan' tidak ditemukan dalam data.")
        return pd.DataFrame()

    # Mapping kategori pendidikan ke standar
    education_map = {
        'SMA': 'SMA',
        'SD KE BAWAH': 'SD KE BAWAH',
        'TIDAK/BELUM PERNAH SEKOLAH': 'SD KE BAWAH',
        'TIDAK/BELUM TAMAT SD': 'SD KE BAWAH',
        'SD': 'SD',
        'SMP': 'SMP',
        'DIPLOMA': 'DIPLOMA/UNIV',
        'UNIVERSITAS': 'DIPLOMA/UNIV',
        'AKADEMI': 'DIPLOMA/UNIV'
    }

    # Fungsi cleaning untuk tiap nilai pendidikan
    def clean_education(x: Any) -> str:
        if not isinstance(x, str):
            return 'UNKNOWN'
        x_upper = x.upper()
        for key, val in education_map.items():
            if key in x_upper:
                return val
        return x_upper

    # Isi nilai kosong di kolom pendidikan dengan 'UNKNOWN'
    df['pendidikan'] = df['pendidikan'].fillna('UNKNOWN')

    # Terapkan fungsi cleaning ke kolom pendidika
    df['pendidikan_bersih'] = df['pendidikan'].apply(clean_education)

    return df

# Load data ke dalam variabel df
df = load_data()

# =========================
# 2. DATA EXPLORATION
# =========================

# Judul utama aplikasi
st.title("📊 Analisis Pengangguran Jawa Barat berdasarkan Pendidikan (2011-2023)")
st.caption("Sumber data: opendata.jabarprov.go.id | Visualisasi: Streamlit")

# Sidebar untuk filter data
st.sidebar.header("Filter Data")
tahun_min, tahun_max = int(df['tahun'].min()), int(df['tahun'].max()) # Tahun minimum dan maksimum pada data
# Slider untuk memilih rentang tahun
tahun_range = st.sidebar.slider("Pilih rentang tahun", tahun_min, tahun_max, (tahun_min, tahun_max), 1)
# List kategori pendidikan
pendidikan_list = ['SD KE BAWAH', 'SD', 'SMP', 'SMA', 'DIPLOMA/UNIV']
# Multiselect untuk memilih pendidikan
pendidikan_pilih = st.sidebar.multiselect("Pilih pendidikan", pendidikan_list, pendidikan_list)

# Filter data berdasarkan tahun dan pendidikan yang dipilih user
df_filtered = df[(df['tahun'] >= tahun_range[0]) & (df['tahun'] <= tahun_range[1])]
df_filtered = df_filtered[df_filtered['pendidikan_bersih'].isin(pendidikan_pilih)]


# =========================
# 3. TAMPILKAN DATA MENTAH
# =========================
with st.expander("Lihat Data Mentah"):
    st.write(df_filtered)  # Tampilkan tabel data hasil filter
    st.markdown(
        """
        Sumber data: [Jumlah Pengangguran Terbuka Berdasarkan Pendidikan di Jawa Barat](https://opendata.jabarprov.go.id/id/dataset/jumlah-pengangguran-terbuka-berdasarkan-pendidikan-di-jawa-barat)
        """
    )

# =========================
# 4. STATISTIK DESKRIPTIF
# =========================

st.subheader("Statistik Deskriptif")
if df_filtered.empty:
    # Jika data kosong, tampilkan info
    st.info("Tidak ada data untuk ditampilkan pada statistik deskriptif.")
else:
    # Tampilkan statistik deskriptif (mean, std, min, max) per pendidikan
    st.dataframe(
        df_filtered.groupby(['pendidikan_bersih'])['jumlah_pengangguran_terbuka']
        .describe()[['mean', 'std', 'min', 'max']].round(0)
    )

# Cek data hilang di seluruh data
missing = df.isnull().sum()
if missing.any():
    st.warning("Ada data hilang:\n" + str(missing[missing>0]))

# Link ke interpretasi
st.markdown("[Lanjut ke Interpretasi Hasil Visualisasi Statistik Deskriptif](#interpretasi-hasil-visualisasi-statistik-deskriptif)")

# =========================
# 5. VISUALISASI TREN
# =========================

st.subheader("Tren Pengangguran Terbuka per Pendidikan")

# Pivot table dari hasil filter sidebar
pivot = df_filtered.pivot_table(
    index='tahun',
    columns='pendidikan_bersih',
    values='jumlah_pengangguran_terbuka',
    aggfunc='sum'
).fillna(0)

# Hanya ambil kolom pendidikan yang tersedia
available_cols = [col for col in pendidikan_list if col in pivot.columns]
pivot = pivot[available_cols]

# Jika data kosong, tampilkan info
if pivot.empty or len(available_cols) == 0:
    st.info("Silakan pilih minimal satu pendidikan dan tahun untuk menampilkan grafik tren pengangguran.")
else:
    # Plot tren pengangguran per pendidikan
    fig, ax = plt.subplots(figsize=(20,5))
    pivot.plot(ax=ax, marker='o')
    ax.set_ylabel("Jumlah Pengangguran")
    ax.set_xlabel("Tahun")
    ax.set_title("Tren Pengangguran Terbuka per Pendidikan")
    ax.legend(title="Pendidikan")
    st.pyplot(fig)

# Link ke interpretasi
st.markdown("[Lanjut ke Interpretasi Hasil Visualisasi Tren](#interpretasi-hasil-visualisasi-tren)")

# =========================
# 6. STACKED BAR CHART
# =========================

st.subheader("Proporsi Pengangguran per Pendidikan (Stacked Bar)")
if pivot.empty or len(available_cols) == 0:
    st.info("Silakan pilih minimal satu pendidikan dan tahun untuk menampilkan grafik proporsi pengangguran.")
else:
        # Hitung proporsi (%) pengangguran per pendidikan per tahun
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    fig2, ax2 = plt.subplots(figsize=(20,5))
    pivot_pct.plot(kind='bar', stacked=True, ax=ax2, colormap='tab20')

    ax2.set_ylabel("Persentase (%)")
    ax2.set_xlabel("Tahun")
    ax2.set_title("Proporsi Pengangguran Terbuka per Pendidikan")

    # Menambahkan label persentase di atas setiap segmen
    for idx, tahun in enumerate(pivot_pct.index):
        cum_height = 0
        for col in pivot_pct.columns:
            height = pivot_pct.loc[tahun, col]
            if height > 0:
                ax2.text(
                    idx, 
                    cum_height + height / 2,  # posisi vertikal di tengah segmen
                    f"{height:.1f}%", 
                    ha='center', 
                    va='center', 
                    fontsize=8,
                    color='white' if height > 5 else 'black'  # warna teks agar kontras
                )
            cum_height += height

    st.pyplot(fig2)

# Link ke interpretasi
st.markdown("[Lanjut ke Interpretasi Hasil Visualisasi Stacked Bar](#interpretasi-hasil-visualisasi-stacked-bar)")

# =========================
# 7. HEATMAP KORELASI
# =========================

st.subheader("Heatmap Korelasi Tahun vs Pengangguran per Pendidikan")
if pivot.empty or len(available_cols) == 0:
    st.info("Tidak ada data untuk membuat heatmap korelasi.")
else:
    corr_df = pivot.fillna(0)
    corr = corr_df.corr()
    fig4, ax4 = plt.subplots(figsize=(20,5))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax4)
    ax4.set_title("Korelasi Jumlah Pengangguran antar Pendidikan")
    st.pyplot(fig4)

# Link ke interpretasi
st.markdown("[Lanjut ke Interpretasi Hasil Visualisasi HeatMap Korelasi](#interpretasi-hasil-visualisasi-heatmap-korelasi)")

# =========================
# 8. REGRESI LINEAR SEDERHANA
# =========================

st.subheader("Regresi Linear Sederhana (Tren Pengangguran per Pendidikan)")
from scipy.stats import linregress

if pivot.empty or len(available_cols) == 0:
    st.info("Tidak ada data untuk regresi linear.")
else:
    # Lakukan regresi linear untuk setiap pendidikan
    for p in available_cols:
        y = pivot[p].dropna()
        x = y.index.values     
        if len(y) > 1:
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            st.info(f"{p}: y = {slope:.0f}x + {intercept:.0f} | R²={r_value**2:.2f} | {'Naik' if slope>0 else 'Turun'}")
# Link ke interpretasi 
st.markdown("[Lanjut ke Interpretasi Hasil Visualisasi Regresi Linear Sederhana](#interpretasi-hasil-visualisasi-regresi-linear-sederhana)")
# =========================
# 9. GROUPED BAR CHART (BAR SAMPINGAN)
# =========================

st.subheader("Jumlah Pengangguran Terbuka per Pendidikan per Tahun (Grouped Bar Chart)")
if pivot.empty or len(available_cols) == 0:
    st.info("Silakan pilih minimal satu pendidikan dan tahun untuk menampilkan grouped bar chart.")
else:
    # Plot grouped bar chart
    fig5, ax5 = plt.subplots(figsize=(18,6))
    bar_width = 0.15
    index = np.arange(len(pivot.index))
    for i, col in enumerate(pivot.columns):
        ax5.bar(index + i*bar_width, pivot[col], bar_width, label=col)
    ax5.set_xlabel('Tahun')
    ax5.set_ylabel('Jumlah Pengangguran')
    ax5.set_title('Jumlah Pengangguran Terbuka per Pendidikan per Tahun (Grouped Bar Chart)')
    ax5.set_xticks(index + bar_width * (len(pivot.columns)-1) / 2)
    ax5.set_xticklabels(pivot.index)
    ax5.legend()
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig5)
# Link ke interpretasi 
st.markdown("[Lanjut ke Interpretasi Hasil Visualisasi Grouped Bar Chart](#interpretasi-hasil-visualisasi-grouped-bar-chart)")

# =========================
# 10. DOWNLOAD DATA & CHART
# =========================

st.sidebar.header("Download")
# Download data hasil filter dalam format CSV
csv = df_filtered.to_csv(index=False).encode()
st.sidebar.download_button("Download Data Filtered (CSV)", csv, "data_filtered.csv", "text/csv")

# Download chart tren sebagai PNG
if not pivot.empty and len(available_cols) > 0:
    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.sidebar.download_button("Download Chart Tren (PNG)", buf.getvalue(), "chart_tren.png", "image/png")

# link github
st.sidebar.markdown("---") # Garis pemisah untuk keterbacaan
st.sidebar.subheader("Kode Sumber Proyek")
st.sidebar.info("[Lihat di GitHub](https://github.com/Firnianoor/uasalgoritma)")


# =========================
# 11. README SINGKAT
# =========================


st.markdown("""
---
## ✍ Interpretasi Hasil Visualisasi Statistik Deskriptif

 Interpretasi dari tabel Statistik Deskriptif Pengangguran Terbuka per Pendidikan
            
**1. Rata-rata Jumlah Pengangguran (mean)**
             

        SMA memiliki rata-rata pengangguran tertinggi: 742.797 orang.

Disusul oleh:
                   
    - SD                     : 454.061        
    - SMP                    : 451.671
    - SD ke Bawah            : 188.510
    - Diploma/Universitas    : 171.853
            
Artinya: 
            
            Lulusan SMA paling rentan mengalami pengangguran terbuka, 
            
Kemungkinan karena terjebak di tengah: 

            Tidak cukup kualifikasi untuk pekerjaan profesional, tetapi terlalu tinggi untuk pekerjaan kasar.

---          

**2. Standar Deviasi (std)**
            
            Nilai std menunjukkan seberapa besar variasi data dari rata-rata.

    - SD (295.966) dan SMA (176.187), 
            menunjukkan fluktuasi besar dalam jumlah pengangguran dari tahun ke tahun.
            -------------------------------------------------------------------------
    - Diploma/Universitas punya fluktuasi paling kecil (103.322), 
            menunjukkan tren yang lebih stabil.
---
            
**3. Nilai Minimum dan Maksimum**
            
    Datanya:
        - SD: Maksimum sangat tinggi (1.272.366), 
            menunjukkan kemungkinan lonjakan ekstrem di tahun tertentu (kemungkinan besar 2020).
            ---------------------------------------------------------------------------------
        - SMA juga tinggi (1.014.084), 
            konsisten dengan grafik tren sebelumnya.
            ---------------------------------------------------------------------------------
        - Diploma/Univ dan SD ke Bawah memiliki nilai maksimum lebih rendah.
---
            
**4. Perbandingan Extremes**
            
    Perbandingannya:
       - Lulusan SD dan SMA 
            menunjukkan potensi risiko pengangguran dalam jumlah besar, apalagi saat terjadi krisis (misalnya pandemi).
            ----------------------------------------------------------------------------------
       - Lulusan Diploma/Universitas 
            lebih stabil dan rendah, menandakan pendidikan tinggi masih menawarkan perlindungan terhadap pengangguran terbuka, meskipun tidak sepenuhnya aman.
---
""")

st.markdown("""
---
## ✍ Interpretasi Hasil Visualisasi Tren 
            
    Interpretasi dari grafik “Tren Pengangguran Terbuka per Pendidikan”

**1. Lulusan SMA Paling Rentan Pengangguran**

    Maksudnya:          
        - Garis merah (SMA) konsisten paling tinggi dibanding jenjang lain dari 2011 hingga 2023.
        - Ini menunjukkan bahwa lulusan SMA paling banyak menganggur.
        - Kemungkinan besar mereka belum melanjutkan ke perguruan tinggi tapi juga tidak langsung terserap ke pasar kerja.

**2. Puncak Pengangguran Tahun 2020**
    
    Maksudnya:
        - Terjadi lonjakan ekstrem pada semua jenjang pendidikan, terutama SMA dan SD.
        - Ini sejalan dengan dampak ekonomi pandemi COVID-19 yang menyebabkan banyaknya PHK dan pembatasan kerja.

**3. Penurunan Setelah 2020**
            
    Maksudnya:
        - Setelah puncak 2020, jumlah pengangguran menurun pada semua tingkat pendidikan.
        - Namun, SMA masih mendominasi angka pengangguran, meskipun trennya menurun perlahan.

**4. Pengangguran Lulusan Diploma/Universitas Tetap Stabil**
            
    Maksudnya:
        - Garis ungu (DIPLOMA/UNIV) berada di bawah SMA, SMP, dan SD.
        - Ini mengindikasikan bahwa lulusan perguruan tinggi memiliki kemampuan kerja lebih tinggi dan lebih terlindungi dari pengangguran terbuka.

5. SD ke Bawah dan SD Relatif Lebih Rendah
            
    Maksudnya:
        - Lulusan SD ke bawah dan SD punya angka pengangguran lebih rendah.
        - Mungkin karena mereka banyak bekerja di sektor informal yang tidak tercatat sebagai pengangguran resmi.
---
""")

st.markdown("""
---
## ✍ Interpretasi Hasil Visualisasi Stacked Bar

Interpretasi Grafik Proporsi Pengangguran Terbuka Berdasarkan Tingkat Pendidikan (2011–2023)
Grafik di atas menampilkan komposisi pengangguran terbuka di jawa barat berdasarkan jenjang pendidikan dari tahun 2011 hingga 2023. Data divisualisasikan dalam bentuk stacked bar (batang bertumpuk), yang menunjukkan proporsi relatif tiap jenjang pendidikan terhadap total pengangguran pada setiap tahunnya.

Jenjang pendidikan dikelompokkan ke dalam lima kategori:
         
    - SD ke bawah
         
    - SD
        
    - SMP
         
    - SMA
         
    - Diploma/Universitas


Temuan Utama:

**Dominasi Pengangguran Lulusan SMA/Sederajat:**
            
     Sepanjang periode 2011–2023, proporsi terbesar pengangguran berasal dari lulusan **SMA/Sederajat**. Misalnya, pada tahun 2023,
    lulusan SMA/Sederajat menyumbang sekitar 56,4% dari total pengangguran terbuka.menunjukkan dominasi yang signifikan. Proporsi ini
     secara konsisten menjadi yang terbesar setiap tahunnya.


**Penurunan Proporsi Pengangguran dari Lulusan Diploma/Universitas**

            
     - Proporsi pengangguran dari lulusan pendidikan tinggi cenderung menurun, dari 7,4% di tahun 2011 menjadi 7,7% di tahun 2023,
     meskipun sempat naik-turun di tengah periode.
    - Ini dapat mencerminkan peningkatan penyerapan lulusan perguruan tinggi oleh pasar kerja, atau pergeseran dalam strategi pencarian kerja oleh lulusan tinggi.

**Kecenderungan Turunnya Proporsi dari SD ke Bawah**

            
     Terlihat adanya penurunan signifikan dalam proporsi pengangguran dari kelompok pendidikan rendah (SD ke bawah), dari 12,4% pada
    2011 menjadi hanya 3,7% di 2018, meski kemudian meningkat menjadi 6,4% di 2020 dan kembali di kisaran 19,3% pada tahun 2023.

**Stabilitas Proporsi SMP**

            
     Proporsi pengangguran dari lulusan SMP relatif stabil, berada di kisaran 15%–28% selama periode yang diamati. Puncaknya terlihat
    pada tahun 2012 dengan 27,9% dan 2013 dengan 27,6%.


**Proporsi Lulusan SD**
            
     Proporsi pengangguran dari lulusan SD juga cukup signifikan, meskipun tidak setinggi SMA. Angka ini berkisar antara 15% hingga
    33% dari total pengangguran. Proporsi tertinggi terlihat pada tahun 2012 (26.3%) dan 2020 (25.4%), menunjukkan bahwa lulusan SD
    masih menghadapi tantangan serius di pasar kerja, terutama di masa krisis.

---
""")

st.markdown("""
---
## ✍ Interpretasi Hasil Visualisasi Heatmap Korelasi


Interpretasi Korelasi antar Jenjang Pendidikan :
            
**1. SD ke Bawah**
            
       Dengan SD → -0.24
            
Artinya, saat pengangguran lulusan SD naik, pengangguran SD ke bawah cenderung turun (hubungan berlawanan).

         Dengan SMP → 0.13
            
Hubungannya sangat lemah (hampir tidak berkaitan).

         Dengan SMA → 0.52

Ada hubungan sedang. Kalau pengangguran SMA naik, SD ke bawah juga bisa naik, tapi tidak terlalu kuat.

          
         Dengan Diploma/Univ → 0.32

Hubungan lemah ke sedang.
            
---

**2. SD**
            
         Dengan SMP → 0.91

Hubungan sangat kuat. Jika pengangguran SMP naik, SD juga hampir pasti naik.

         Dengan SMA → 0.47
            
Hubungan cukup kuat, tapi tidak sekuat dengan SMP.

         Dengan Diploma/Univ → 0.67

Hubungan kuat.
            
---

**3. SMP**
            
         Dengan SMA → 0.60
            
Korelasi kuat.

         Dengan Diploma/Univ → 0.73
            
Korelasi sangat kuat. Artinya tren pengangguran mereka sangat mirip.
            
---

**4. SMA**
            
         Dengan Diploma/Univ → 0.94

Inilah korelasi tertinggi antar jenjang berbeda di heatmap ini. Artinya, pengangguran SMA dan Diploma/Univ cenderung selalu naik/turun bersamaan.

---
            
**5. Diploma/Univ**

         Korelasi tertinggi dengan SMA (0.94), lalu SMP (0.73), dan SD (0.67).

Korelasi terendah dengan SD ke bawah (0.32).

            
---
""")

st.markdown("""
---
## ✍ Interpretasi Hasil Visualisasi Regresi Linear Sederhana
Interpretasi berikut merangkum hasil analisis regresi linear sederhana untuk masing-masing jenjang pendidikan. Setiap bagian menampilkan persamaan regresi, nilai R-squared, dan tren yang dihasilkan.

---

**1. SD ke bawah**
    
     SD KE BAWAH : y = 24434x + -49066609 | R²=0,37 | Naik

Regresi persamaan: y = 24434x - 49066609.
Hal ini menunjukkan bahwa untuk setiap peningkatan satu tahun (variabel independen 'x' adalah tahun), **jumlah pengangguran terbuka** untuk kelompok SD ke bawah cenderung meningkat sebesar 24.434 orang.
Intersep -49.066.609 adalah nilai prediksi jumlah pengangguran ketika tahun bernilai nol (ini adalah proyeksi matematis dan mungkin tidak memiliki makna praktis langsung, karena tahun 0 jauh dari data kita).


     R-kuadrat (R²): 0,37.
Sekitar 37% variasi **jumlah pengangguran terbuka** SD ke bawah dapat dijelaskan oleh model regresi ini. Sisanya dipengaruhi faktor lain.

     Tren: Naik.
            
Artinya, tren **jumlah pengangguran terbuka** SD ke bawah cenderung meningkat seiring waktu.

---
            
**2. SD**
            
     SD : y = -21897x + 44515094 | R²=0,07 | Turun

Persamaan Regresi: y = -21897x + 44515094.
Setiap kenaikan satu tahun pada variabel independen cenderung menurunkan **jumlah pengangguran terbuka** lulusan SD sebesar 21.897 orang.

     R-kuadrat (R²): 0,07.
Sekitar 7% variasi **jumlah pengangguran terbuka** SD dapat dijelaskan oleh model ini; hubungan sangat lemah.

     Tren: Turun.
            
**Jumlah pengangguran terbuka** lulusan SD cenderung menurun seiring berjalannya waktu.


**3. SMP/Sederajat**
            
     SMP : y = -5442x + 11428684 | R²=0,02 | Turun

Persamaan Regresi: y = -5442x + 11428684.
Setiap kenaikan satu tahun pada variabel independen cenderung menurunkan **jumlah pengangguran terbuka** lulusan SMP sebesar 5.442 orang.

     R-kuadrat (R²): 0,02.
Hanya 2% variasi **jumlah pengangguran terbuka** SMP yang dijelaskan model ini; hubungan sangat lemah.

     Tren: Turun.
            
**Jumlah pengangguran terbuka** lulusan SMP cenderung menurun seiring berjalannya waktu.

---

**4. SMA/Sederajat**
            
     SMA: y = 64566x - 129258105 | R² = 0,46 | Naik

Regresi Persamaan: y = 64566x - 129258105.
Setiap kenaikan satu tahun pada variabel independen meningkatkan **jumlah pengangguran terbuka** lulusan SMA sebesar 64.566 orang.

     R-kuadrat (R²): 0,46.
Sekitar 46% variasi **jumlah pengangguran terbuka** SMA dapat dijelaskan model ini; hubungan moderat-kuat.
            
     Tren: Naik.

**Jumlah pengangguran terbuka** lulusan SMA cenderung meningkat seiring waktu.

---

**5. D3/S1/Sederajat**
     DIPLOMA/UNIV: y = 12211x + -24457368 | R²=0,21 | Naik

Regresi Persamaan: y = 12211x - 24457368.
Setiap kenaikan satu tahun pada variabel independen meningkatkan **jumlah pengangguran terbuka** diploma/Universitas sebesar 12.211 orang.

     R-kuadrat (R²): 0,21.
Sekitar 21% variasi **jumlah pengangguran terbuka** pendidikan Diploma/Universitas dijelaskan model ini; hubungan lemah-moderat.

     Tren: Naik.
            
**Jumlah pengangguran terbuka** lulusan Diploma/Universitas cenderung meningkat seiring waktu.
                           
---
""")

st.markdown("""
---
## ✍ Interpretasi Hasil Visualisasi Grouped Bar Chart

**1. Deskripsi Umum Grafik**

Grafik ini menyajikan data jumlah pengangguran terbuka berdasarkan tingkat pendidikan dari tahun 2011 hingga 2023. Setiap tahun ditampilkan dalam bentuk kelompok batang (*grouped bar*), masing-masing mewakili jenjang pendidikan berikut:

            

        Biru   : SD ke bawah
            
    Oranye : SD

    Hijau  : SMP

    Merah  : SMA
            
    Ungu   : Diploma/Universitas


Sumbu vertikal menunjukkan jumlah pengangguran (dalam jutaan orang), dan sumbu horizontal menunjukkan tahun (2011–2023).

---

**2. Pola dan Tren Tiap Jenjang Pendidikan**

A. Lulusan SMA (Merah)

     Selalu menjadi kelompok dengan tingkat penurunan tertinggi setiap tahun.

    Puncaknya pada tahun 2020: lebih dari 2 juta kemiskinan.


Setelah tahun 2020, jumlahnya turun tetapi masih paling tinggi dibandingkan jenjang lain:
     
     2021: sekitar 1,5 juta
            
    2022: sekitar 1,45 juta
            
    2023: sekitar 1,4 juta

B. Lulusan SMP (Hijau)

     Umumnya berada di posisi kedua atau ketiga tertinggi.

    Terakhir mengalami peningkatan cukup tajam pada tahun 2020: sekitar 1 juta penurunan.

Setelah tahun 2020, terjadi penurunan:
            
     2021: ±800 ribu
            
    2023: ±750 ribu

C. Lulusan SD (Orange)

     Cenderung stabil sebelum tahun 2020 (sekitar 300–450 ribu).

    Lonjakan besar pada tahun 2020: sekitar 1,2 juta penurunan.

Setelah itu menurun:
            
     2021: ±600 ribu
            
    2023: ±550 ribu

D. SD ke Bawah (Biru)

     Jumlah kemiskinan paling rendah selama 2011–2019.

Namun meningkat signifikan setelah pandemi:
            
     2020: ±400 ribu
            
    2021: ±650 ribu (tertinggi sepanjang periode untuk peningkatan ini)
            
    2023: ±600 ribu

E. Diploma/Universitas (Ungu)

     Konsisten sebagai peningkatan dengan kemiskinan menengah.

Tidak terlalu fluktuatif kecuali di 2020:

     2020: ±650 ribu

    2023: turun ke ±300 ribu


---

**3. Tahun Spesial: 2020**

Semua peningkatan mengalami penurunan tingkat kemiskinan yang signifikan, terutama:

     SMA: naik drastis ke ±2,1 juta

    SD: naik menjadi ±1,2 juta

    SMP: naik menjadi ±1 juta

kemungkinan besar karena dampak pandemi COVID-19 yang menyebabkan PHK massal dan kesulitan pasar kerja.           

---
""")
# =========================
# 12. KESIMPULAN
# =========================

st.subheader("KESIMPULAN")

if df_filtered.empty:
    st.info("Tidak ada data untuk insight otomatis pada filter ini.")
else:

    # Dapatkan pendidikan dengan rata-rata pengangguran tertinggi pada filter saat ini
    avg_pengangguran = df_filtered.groupby('pendidikan_bersih')['jumlah_pengangguran_terbuka'].mean()
    pendidikan_tertinggi = avg_pengangguran.idxmax() # Pendidikan dengan rata-rata pengangguran tertinggi
    rata_rata_tertinggi = avg_pengangguran.max() # Nilai rata-rata tertinggi
    
    # Cari tahun dengan pengangguran terbuka tertinggi pada data hasil filter
    tahun_tertinggi = df_filtered.loc[df_filtered['jumlah_pengangguran_terbuka'].idxmax()]['tahun']

    st.markdown(f"""
**Analisis ini membahas kondisi pengangguran terbuka di Jawa Barat dari tahun {tahun_range[0]} sampai {tahun_range[1]}, dilihat dari tingkat pendidikan terakhir para pencari kerja. Tujuannya untuk memahami siapa yang paling banyak menganggur dan bagaimana tren pengangguran berubah berdasarkan jenjang pendidikan.**

Salah satu hasil utama adalah lulusan **SMA/Sederajat** merupakan kelompok dengan pengangguran terbanyak, dengan rata-rata tertinggi dibanding jenjang lain. Kategori ini mencakup lulusan SMA umum dan juga **SMK**. Tingginya angka pengangguran di kelompok ini mungkin karena mereka berada di posisi "tanggung"—seringkali tidak memiliki keahlian teknis yang sangat spesifik seperti jenjang pendidikan tinggi, namun juga memiliki ekspektasi yang berbeda dari pekerjaan di sektor informal.

Lulusan perguruan tinggi (Diploma/Sarjana) memiliki jumlah pengangguran lebih sedikit dan cenderung stabil, menandakan semakin tinggi pendidikan, peluang mendapatkan pekerjaan yang sesuai cenderung lebih besar meskipun tidak 100% terjamin.

Tahun **{tahun_tertinggi}** adalah puncak pengangguran di semua jenjang pada rentang tahun yang dipilih, akibat dampak pandemi COVID-19 yang menyebabkan banyaknya PHK dan pembatasan aktivitas ekonomi. Setelah 2020, jumlah pengangguran menurun pada umumnya, tetapi lulusan SMA/Sederajat tetap mendominasi angka pengangguran.

Dari data proporsi pengangguran, lulusan SMA/Sederajat selalu mendominasi persentase total pengangguran, sementara proporsi pengangguran dari lulusan SD ke bawah dan perguruan tinggi cenderung lebih kecil. Lulusan SD ke bawah seringkali banyak terserap di sektor informal yang tidak selalu tercatat sebagai pengangguran resmi.

Analisis korelasi menunjukkan bahwa saat pengangguran lulusan SMA/Sederajat naik, pengangguran lulusan perguruan tinggi juga cenderung naik. Ini mengindikasikan bahwa dampak kondisi ekonomi tertentu dapat meluas dan mempengaruhi semua jenjang pendidikan, terutama menengah dan tinggi.

Prediksi regresi linear menunjukkan:
1. Pengangguran lulusan SMA/Sederajat dan SD ke bawah diperkirakan terus naik.
2. Lulusan SMP diperkirakan mengalami penurunan pengangguran, meskipun prediksinya lemah.
3. Lulusan pendidikan tinggi diprediksi mengalami kenaikan kecil dan stabil.

Kesimpulannya, pengangguran paling banyak terjadi pada lulusan **pendidikan menengah atas (SMA/Sederajat)**. Lulusan perguruan tinggi memiliki tingkat pengangguran yang lebih rendah dan tren lebih stabil. Sementara itu, lulusan pendidikan rendah kemungkinan besar banyak bekerja di sektor informal dan tidak tercatat secara resmi.

Oleh karena itu, perlu perbaikan kurikulum di jenjang pendidikan menengah atas (baik SMA maupun SMK) agar lebih sesuai dengan kebutuhan dunia kerja. Penting juga untuk mendorong kerjasama yang lebih erat antara institusi pendidikan dan industri, serta memberikan insentif agar lulusan SMA/Sederajat melanjutkan pendidikan atau mengikuti program pelatihan kerja untuk memperoleh keterampilan yang dibutuhkan pasar.

**Pada filter saat ini:**
- **Rata-rata pengangguran terbuka tertinggi berasal dari pendidikan:** `{pendidikan_tertinggi}` (rata-rata: {rata_rata_tertinggi:,.0f})
- **Tahun dengan pengangguran terbuka tertinggi:** `{tahun_tertinggi}`
""")
