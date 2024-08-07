import pandas as pd
import re

# Daftar brand mobil
brand_list = [
    "BMW", "Honda", "Hyundai", "Mercedes-Benz", "Mitsubishi", "Suzuki", "Toyota", "Wuling", "Abarth", "Aro",
    "Aston Martin", "Audi", "Bentley", "Cadillac", "Chery", "Chevrolet", "Chrysler", "Citroen", "Daihatsu",
    "Datsun", "DFSK", "Dodge", "Ferrari", "Fiat", "Ford", "Geely", "Genesis", "Great Wall Motor", "Hino",
    "Holden", "Hummer", "Infiniti", "Isuzu", "Jaguar", "Jeep", "KIA", "Lamborghini", "Land Rover", "Lexus",
    "Maserati", "Mazda", "McLaren", "MG", "MINI", "Mitsubishi Colt", "Morgan", "Nissan", "Opel", "Peugeot",
    "Porsche", "Proton", "Renault", "Rolls-Royce", "smart", "SsangYong", "Subaru", "Tata", "Tesla", "Timor",
    "UD TRUCKS", "Volkswagen", "Volvo"
]

# Daftar jenis mobil
jenis_mobil_list = [
    'SUV', 'MPV', 'Hatchback', 'Wagon', 'Sedan', 'Van Wagon', 'Coupe', 'Pick-up', 'Van', 'Trucks', 'Convertible',
    'Gran Coupe', 'MPV Minivans', 'Jeep', 'Cabriolet', 'Fastback', 'Compact Car City Car', 'Minibus', 'Pick Up',
    'Sportback', 'Targa', 'Lainnya', 'SUV Offroad 4WD', 'Convertibles Roadsters', 'Box', 'Double Cabin', 'Full Bus'
]

# Fungsi untuk mengekstrak nilai jenis mobil dari nama mobil
def extract_jenis_mobil(nama_mobil):
    for jenis in jenis_mobil_list:
        if jenis.lower() in nama_mobil.lower():
            return jenis
    return "Jenis tidak ditemukan"

# Fungsi untuk mengekstrak nama brand dari nama mobil
def extract_brand_name(nama_mobil, brand_list):
    for brand in brand_list:
        if brand in nama_mobil:
            return brand
    return None

# Fungsi untuk membersihkan data kilometer dari penjelasan "km" dan spasi
def clean_kilometer_interval(interval):
    return re.sub(r'\s*km\s*', '', interval)

# Fungsi untuk membersihkan data dari penjelasan "K" dan konversi ke nilai ribuan
def clean_and_convert_to_thousand(interval):
    interval_cleaned = re.sub(r'\s*K\s*', '', interval)
    if ' - ' in interval_cleaned:
        start, end = map(int, interval_cleaned.split(' - '))
        return f"{start * 1000}-{end * 1000}"
    else:
        return interval_cleaned

# Fungsi untuk mengubah interval menjadi nilai rata-rata bulat
def interval_to_average(interval):
    if '-' in interval:
        start, end = map(int, interval.split('-'))
        return round((start + end) / 2)
    else:
        return int(interval)

# Fungsi untuk memisahkan nilai pertama dari string
def nilai_awal(nilai):
    nilai_awal = nilai.split(' ')[0]
    return nilai_awal.strip()

# Fungsi untuk memisahkan nilai kedua dari string
def nilai_kedua(nilai):
    nilai_kedua = nilai.split(' ')[1]
    return nilai_kedua.strip()

# Fungsi untuk membersihkan dan mengkonversi nilai string ke integer
def clean_and_convert_to_int(value):
    cleaned_value = re.sub(r'\.', '', value)
    return int(cleaned_value)

# Fungsi untuk melakukan preprocessing data
def preprocess_data(df):
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    
    df['jenis_mobil'] = df['Title'].apply(extract_jenis_mobil)
    df = df[df['jenis_mobil'] != 'Jenis tidak ditemukan']

    df['brand'] = df['Title'].apply(lambda x: extract_brand_name(x, brand_list))
    df.dropna(subset=['brand'], inplace=True)

    df['Kilometer'] = df['Kilometer'].apply(clean_kilometer_interval)
    df['Kilometer'] = df['Kilometer'].apply(clean_and_convert_to_thousand)
    df['Kilometer'] = df['Kilometer'].apply(interval_to_average)
    df['Kilometer'] = df['Kilometer'].astype(int)

    df["Harga"] = df["Harga"].apply(nilai_kedua)
    df["Harga"] = df["Harga"].apply(clean_and_convert_to_int)
    df["Cakupan mesin"] = df["Cakupan mesin"].apply(nilai_awal)
    df['Cakupan mesin'] = df['Cakupan mesin'].replace('cc', '0')
    df['Cakupan mesin'] = df['Cakupan mesin'].astype(int)

    df.drop(columns=['Title', 'Kondisi'], inplace=True)

    # Mengubah nama kolom sesuai dengan yang diinginkan
    df.rename(columns={
        'Tahun Kendaraan': 'tahun_kendaraan',
        'Warna': 'warna',
        'Transmisi': 'transmisi',
        'Kilometer': 'kilometer',
        'Cakupan mesin': 'mesin_enginecc',
        'Tipe Bahan Bakar': 'bahan_bakar',
        'Dirakit': 'dirakit',
        'Penumpang': 'penumpang',
        'Pintu': 'pintu',
        'Harga': 'harga'
    }, inplace=True)

    # Mengatur urutan kolom
    ordered_columns = ['brand', 'jenis_mobil', 'tahun_kendaraan', 'warna', 'transmisi', 'kilometer', 'mesin_enginecc', 'bahan_bakar', 'dirakit', 'penumpang', 'pintu', 'harga']
    df = df[ordered_columns]

    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    # Menyimpan hasil preprocessing ke file CSV
    df.to_csv('data/clean_data.csv', index=False)

    return df
