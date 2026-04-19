# Urban Longevity: NYC Green Infrastructure Dashboard

**A Data-Driven Predictive Tool for Urban Health Equity.**

## 🏥 The Problem
Air quality (PM2.5) and lack of green canopy are directly correlated with higher asthma rates in New York City. City planners often lack a unified, predictive tool to visualize how specific green infrastructure investments (tree planting) can mitigate these public health crises at the Zip Code level.

## 🌳 The Solution: Urban Longevity
Urban Longevity is an MVP dashboard that allows NYC planners to:
1. **Identify High-Risk Zones:** A weighted "Need Index" correlates tree density, PM2.5 levels, and asthma discharges to highlight priority areas.
2. **Predict Impact:** An interactive "Prediction Slider" uses inverse-correlation logic to simulate how planting trees reduces PM2.5 levels and predicted asthma rates.
3. **Actionable Intelligence:** A spatial heuristic recommends specific tree species (e.g., Japanese Zelkova for high-density areas) based on current canopy stats.

## 🚀 Features
* **Interactive Mapbox Visualization:** Real-time rendering of NYC Zip Codes using `carto-darkmatter` styling.
* **Weighted Need Index:** Algorithmic prioritization using normalized health and environmental data.
* **Dynamic Prediction Engine:** Real-time UI updates to asthma risk profiles based on simulated canopy growth.
* **Priority Intervention Table:** A sorted, actionable list for policymakers including recommended tree species.

## 🛠️ Tech Stack
* **Language:** Python
* **Frontend/UI:** Streamlit
* **Data Science:** Pandas (ETL & Analysis), NumPy (Normalization)
* **Visuals:** Plotly Express (Mapbox & Scatter Plots)

## 📊 Data Sources
* **NYC Open Data:** Tree Census Data, Environment & Health (Asthma Discharges).
* **Kaggle:** Historical Air Quality (PM2.5) datasets.

## ⚙️ Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/lainx06/urban-longevity.git](https://github.com/lainx06/urban-longevity.git)
   cd urban-longevity

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Run the Dashboard:**
   ```bash
   streamlit run main.py

## 🧠 Technical Methodology
To determine intervention priority, we calculate a Need Index:

$$Need Index = (0.6 \times Asthma_{norm}) + (0.4 \times PM2.5_{norm})$$

The prediction engine assumes an inverse relationship between canopy density and respiratory triggers, providing a visual "what-if" scenario for urban reforestation.

## 🔮 Future Roadmap
* **Heat-Island Correlation:** Integrate surface temperature data to show cooling effects.
* **Machine Learning Integration:** Replace linear correlations with a Random Forest Regressor for more accurate longitudinal predictions.
* **Financial ROI:** Add a module to calculate healthcare cost savings per 100 trees planted.
