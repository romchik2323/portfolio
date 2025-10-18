
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score




DB_CONFIG = {
    'host': 'localhost',
    'database': 'telco_churn1', 
    'user': 'admin',
    'password': '1234',
    'port': '5432'
}

try:
    engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
except Exception as e:
    print(f"Ошибка подключения: {e}")
    exit()


try:
    df = pd.read_sql("SELECT * FROM customers", engine)
    
except Exception as e:
    
    exit()



df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
df['totalcharges'] = df['totalcharges'].fillna(0)

# Создаем бинарные признаки
df['churn_numeric'] = (df['churn'] == 'Yes').astype(int)
df['is_month_to_month'] = (df['contract'] == 'Month-to-month').astype(int)
df['has_fiber'] = (df['internetservice'] == 'Fiber optic').astype(int)
df['no_tech_support'] = (df['techsupport'] == 'No').astype(int)
df['has_partner'] = (df['partner'] == 'Yes').astype(int)
df['has_dependents'] = (df['dependents'] == 'Yes').astype(int)
df['is_senior'] = df['seniorcitizen']
df['is_paperless'] = (df['paperlessbilling'] == 'Yes').astype(int)




print(f"Всего клиентов: {len(df):,}")
print(f"Ушло клиентов: {(df['churn'] == 'Yes').sum():,}")
print(f"Процент оттока: {(df['churn'] == 'Yes').mean():.1%}")

print(f"\nВремя с компанией:")
print(f"   Среднее: {df['tenure'].mean():.1f} месяцев")
print(f"   Максимум: {df['tenure'].max()} месяцев")
print(f"   Минимум: {df['tenure'].min()} месяцев")

print(f"\nПлатежи:")
print(f"   Средний месячный: ${df['monthlycharges'].mean():.2f}")
print(f"   Средний общий: ${df['totalcharges'].mean():.2f}")



# Аналитика по категориальным признакам
def analyze_churn_by_category(column_name, title):
    churn_rates = df.groupby(column_name)['churn_numeric'].mean() * 100
    total_counts = df.groupby(column_name).size()
    
    print(f"\n{title}:")
    for category in churn_rates.index:
        print(f"   {category}: {churn_rates[category]:.1f}% ({total_counts[category]} клиентов)")
    return churn_rates

# Анализ по основным факторам
contract_churn = analyze_churn_by_category('contract', 'ОТТОК ПО КОНТРАКТАМ')
internet_churn = analyze_churn_by_category('internetservice', 'ОТТОК ПО ИНТЕРНЕТУ')
tech_churn = analyze_churn_by_category('techsupport', 'ОТТОК ПО ТЕХПОДДЕРЖКЕ')
payment_churn = analyze_churn_by_category('paymentmethod', 'ОТТОК ПО СПОСОБУ ОПЛАТЫ')



plt.style.use('default')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('АНАЛИЗ ОТТОКА КЛИЕНТОВ', fontsize=16, fontweight='bold')

# График Отток по контрактам
axes[0,0].bar(contract_churn.index, contract_churn.values, 
              color=['red', 'orange', 'green'], alpha=0.7)
axes[0,0].set_title('Отток по контрактам', fontweight='bold')
axes[0,0].set_ylabel('Процент ушедших (%)')
axes[0,0].tick_params(axis='x', rotation=45)
axes[0,0].grid(axis='y', alpha=0.3)
for i, v in enumerate(contract_churn.values):
    axes[0,0].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

# График Отток по интернету
axes[0,1].bar(internet_churn.index, internet_churn.values,
              color=['red', 'pink', 'lightblue'], alpha=0.7)
axes[0,1].set_title('Отток по типу интернета', fontweight='bold')
axes[0,1].set_ylabel('Процент ушедших (%)')
axes[0,1].tick_params(axis='x', rotation=45)
axes[0,1].grid(axis='y', alpha=0.3)
for i, v in enumerate(internet_churn.values):
    axes[0,1].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

# График Отток по техподдержке
axes[0,2].bar(tech_churn.index, tech_churn.values,
              color=['red', 'lightgreen', 'gray'], alpha=0.7)
axes[0,2].set_title('Отток по техподдержке', fontweight='bold')
axes[0,2].set_ylabel('Процент ушедших (%)')
axes[0,2].tick_params(axis='x', rotation=45)
axes[0,2].grid(axis='y', alpha=0.3)
for i, v in enumerate(tech_churn.values):
    axes[0,2].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

# График Распределение tenure
axes[1,0].hist(df['tenure'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
axes[1,0].set_title('Распределение времени с нами', fontweight='bold')
axes[1,0].set_xlabel('Месяцы (tenure)')
axes[1,0].set_ylabel('Количество клиентов')
axes[1,0].grid(alpha=0.3)

# График Средние платежи по оттоку
payment_by_churn = df.groupby('churn').agg({
    'monthlycharges': 'mean',
    'totalcharges': 'mean'
}).reset_index()

x = range(len(payment_by_churn))
width = 0.35

axes[1,1].bar(x, payment_by_churn['monthlycharges'], width, 
              label='Средний месячный', alpha=0.7, color='blue')
axes[1,1].bar([i + width for i in x], payment_by_churn['totalcharges']/100, width, 
              label='Общий/100', alpha=0.7, color='orange')
axes[1,1].set_title('Средние платежи', fontweight='bold')
axes[1,1].set_xticks([i + width/2 for i in x])
axes[1,1].set_xticklabels(payment_by_churn['churn'])
axes[1,1].set_ylabel('Доллары ($)')
axes[1,1].legend()
axes[1,1].grid(axis='y', alpha=0.3)

# График Отток по дополнительным услугам
services = ['onlinesecurity', 'onlinebackup', 'deviceprotection', 'streamingtv', 'streamingmovies']
service_churn = {}

for service in services:
    service_churn[service] = df.groupby(service)['churn_numeric'].mean() * 100

service_names = ['Безопасность', 'Бэкап', 'Защита устройств', 'ТВ', 'Фильмы']
no_service_churn = [service_churn[s]['No'] for s in services]

axes[1,2].bar(service_names, no_service_churn, color='lightcoral', alpha=0.7)
axes[1,2].set_title('Отток без дополнительных услуг', fontweight='bold')
axes[1,2].set_ylabel('Процент ушедших (%)')
axes[1,2].tick_params(axis='x', rotation=45)
axes[1,2].grid(axis='y', alpha=0.3)
for i, v in enumerate(no_service_churn):
    axes[1,2].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('churn_analysis_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()




# Подготовка данных для ML
features = [
    'tenure', 'monthlycharges', 'totalcharges',
    'is_month_to_month', 'has_fiber', 'no_tech_support',
    'is_senior', 'has_partner', 'has_dependents', 'is_paperless'
]

X = df[features]
y = df['churn_numeric']

# Разделение на тренировочную и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Данные для ML:")
print(f"   Признаки: {len(features)}")
print(f"   Тренировочная выборка: {X_train.shape[0]} клиентов")
print(f"   Тестовая выборка: {X_test.shape[0]} клиентов")

# Обучение модели
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)




y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]


print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

# Матрица ошибок
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
           xticklabels=['Остался', 'Ушел'],
           yticklabels=['Остался', 'Ушел'])
plt.title('Матрица ошибок модели', fontweight='bold')
plt.ylabel('Реальность')
plt.xlabel('Предсказание')
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
plt.show()


feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(feature_importance['feature'], feature_importance['importance'])
plt.title('Важность признаков в модели', fontweight='bold')
plt.xlabel('Важность')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nВАЖНОСТЬ ПРИЗНАКОВ:")
for i, row in feature_importance.iterrows():
    print(f"   {row['feature']}: {row['importance']:.3f}")



print("\nКЛЮЧЕВЫЕ ФАКТОРЫ РИСКА:")
print(f"   1. Помесячный контракт: {contract_churn['Month-to-month']:.1f}% оттока")
print(f"   2. Оптоволоконный интернет: {internet_churn['Fiber optic']:.1f}% оттока") 
print(f"   3. Отсутствие техподдержки: {tech_churn['No']:.1f}% оттока")
print(f"   4. Электронные платежи: {payment_churn['Electronic check']:.1f}% оттока")

# Анализ клиентов высокого риска
high_risk = df[
    (df['is_month_to_month'] == 1) & 
    (df['has_fiber'] == 1) &
    (df['no_tech_support'] == 1)
]


print(f"   • Количество: {len(high_risk)} клиентов")
print(f"   • Отток: {high_risk['churn_numeric'].mean():.1%}")
print(f"   • Средний месячный платеж: ${high_risk['monthlycharges'].mean():.2f}")


for i, (idx, prob) in enumerate(zip(sample_data.index, predictions)):
    customer_id = df.loc[idx, 'customerid']
    tenure = df.loc[idx, 'tenure']
    contract = df.loc[idx, 'contract']
    
    risk_level = "ВЫСОКИЙ РИСК" if prob > 0.5 else "НИЗКИЙ РИСК"
    action = "СРОЧНО ЗАДЕРЖИВАТЬ!" if prob > 0.5 else "Все в порядке"
    
    print(f"   Клиент {customer_id}:")
    print(f"   • {tenure} месяцев, контракт: {contract}")
    print(f"   • Вероятность ухода: {prob:.1%} - {risk_level}")
    print(f"   • Рекомендация: {action}")
    

