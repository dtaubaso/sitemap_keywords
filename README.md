# Visualizar las palabras más usadas en sitios de noticias, tomando los títulos desde el Sitemap de News o el feed RSS

Basado en https://github.com/eliasdabbas/news_sitemaps_visualization

Script para visualizar las **palabras más usadas** por cada medio seleccionado en el momento, y comparar los **temas de interés**.

![image](https://user-images.githubusercontent.com/49786545/168337417-d73197f8-95a9-4500-a0b9-34dbbba439fb.png)


## Cómo usarlo

El script usa **Flask** para generar una página web y necesita una **cuenta de servicio** con acceso a Google Sheets ya que toma los datos desde ahí. 

El titulo del Spreadsheet lo utiliza como subdirectorio, si corro el script localmente y mi sheet se llama "sitemap_news", entonces
al ingresar a http://127.0.0.1:5001/sitemap_news va a buscar ese sheet y va a extraer la información de ahí para generar los gráficos.

El sheet debe tener los campos "url" con la url del feed, "name" con el nombre del medio y "category" con el tipo de feed, sea Sitemap News o RSS.

![image](https://user-images.githubusercontent.com/49786545/168337030-a669b356-fd2c-4ee8-aeb0-06d0df4d531e.png)

La página se regenera cada vez que ingreso o recargo, y además tiene selectores para ver los gráficos con 1 o dos ngramas. Por defecto, muestra
la combinación de 1 y 2 ngramas ordenados por frecuencia de aparición.



