import streamlit as st
import pandas as pd
import requests
import time

st.title("Парсер отзывов из App Store 🍏")
st.write("Сбор отзывов (1-3 звезды) из российского сегмента App Store.")

app_id = st.text_input("Введите ID приложения:", "570060128")

if st.button("Собрать отзывы"):
    st.info("Подключаемся к API Apple. Пожалуйста, подождите...")
    reviews_data = []
    progress_bar = st.progress(0)

    try:
        for page in range(1, 11):
            url = f'https://itunes.apple.com/ru/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json'
            response = requests.get(url)
            if response.status_code != 200: break
            data = response.json()
            if 'entry' not in data.get('feed', {}): break

            for entry in data['feed']['entry']:
                if 'author' not in entry: continue 
                rating = int(entry.get('im:rating', {}).get('label', 0))
                if rating in [1, 2, 3]:
                    reviews_data.append({
                        'Дата': entry.get('updated', {}).get('label', ''),
                        'Пользователь': entry.get('author', {}).get('name', {}).get('label', ''),
                        'Оценка': rating,
                        'Заголовок': entry.get('title', {}).get('label', ''),
                        'Текст отзыва': entry.get('content', {}).get('label', ''),
                        'Версия приложения': entry.get('im:version', {}).get('label', 'Не указана')
                    })

            progress_bar.progress(page * 10)
            time.sleep(0.5) 

        if reviews_data:
            df = pd.DataFrame(reviews_data)
            st.success(f"Готово! Собрано {len(df)} отзывов с оценками 1-3 звезды.")
            st.dataframe(df)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="Скачать таблицу (CSV)", data=csv, file_name=f'bad_reviews_{app_id}.csv', mime='text/csv')
        else:
            st.warning("Отзывы с такими оценками не найдены.")
    except Exception as e:
        st.error(f"Произошла ошибка: {e}")
