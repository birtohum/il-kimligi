# İlin Kimliği

**Site:** https://birtohum.github.io/il-kimligi/

81 plaka, 81 sayfa. İlinin nüfusu, göçü, havası, depremi, yangını, gece ışığı, sokak adları ve soyadları tek sayfada; 81 il içinde kaçıncı olduğuyla.

`araclar/uret.py` kendi sitelerimin yayımladığı veriyi okur, her il için statik bir sayfa üretir ve haftada bir yeniden derlenir. Veri toplamaz; kaynaklar ve sınırlar ilgili sitelerde:

| Ölçü | Site | Kaynak |
|---|---|---|
| Nüfus, net göç | [goc-haritasi](https://birtohum.github.io/goc-haritasi/) | TÜİK |
| Soyadları | [soyadin-nereli](https://birtohum.github.io/soyadin-nereli/) | TÜİK |
| Hava | [kac-sigara](https://birtohum.github.io/kac-sigara/) | Bakanlık istasyonları |
| Deprem | [turkiye-sallandi](https://birtohum.github.io/turkiye-sallandi/) | EMSC, AFAD, Kandilli |
| Yangın | [orman-yanginlari-uzaydan](https://birtohum.github.io/orman-yanginlari-uzaydan/) | NASA FIRMS |
| Gece ışığı | [turkiye-geceleri](https://birtohum.github.io/turkiye-geceleri/) | VIIRS |
| Sokak adları | [sokak-adlari](https://birtohum.github.io/sokak-adlari/) | OpenStreetMap |
| Gün doğumu | [gunes-kacta-doguyor](https://birtohum.github.io/gunes-kacta-doguyor/) | NOAA denklemleri |

Sınırlar: hava sıralaması yalnız yeterli ölçümü olan illeri, kadın oranı yalnız en az 200 kişi adlı sokağı olan illeri kapsar. Küçük depremlerin sayısını istasyon sıklığı, sokak sayılarını OpenStreetMap kapsamı etkiler; sıralamalar kesin değil, eğilim gösterir.

[Bütün tablo (CSV)](site/veri/iller.csv). Kod: MIT. Türetilen sokak verisi ODbL (© OpenStreetMap katkıcıları), TÜİK verisi kaynak gösterilerek.
