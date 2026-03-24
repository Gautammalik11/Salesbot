# 🚀 Quick Start Guide

Get your Sales Data Chatbot up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation

### Option 1: Automated Setup (Recommended)

```bash
cd sales-chatbot
./setup.sh
```

This script will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file

### Option 2: Manual Setup

```bash
cd sales-chatbot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## Configuration

1. Open the `.env` file:
```bash
nano .env  # or use any text editor
```

2. Add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

3. Save and close the file

## Running the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run Streamlit
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Testing with Sample Data

We've included a sample dataset for testing:

1. Go to **📤 Upload Data** page
2. Select **Odoo** or **Focus** as the ERP source
3. Upload the `sample_data.csv` file
4. Click **Import Data**

## Usage Guide

### 1️⃣ Upload Your Data

1. Navigate to **📤 Upload Data**
2. Select your ERP source (Odoo or Focus)
3. Upload your CSV file
4. Preview the data
5. Click **Import Data**

### 2️⃣ Chat with Your Data

1. Navigate to **💬 Chat**
2. Ask questions like:
   - "What is the total revenue?"
   - "Show me top 10 customers"
   - "Which products sold the most?"

### 3️⃣ View Analytics

1. Navigate to **📊 Analytics**
2. Apply filters (date range, ERP source)
3. Explore interactive charts
4. Export data as CSV

## Example Questions

Once you have data imported, try these questions in the chat:

**Revenue Queries:**
- What is the total revenue?
- Show me revenue by month
- Compare Odoo vs Focus sales

**Customer Queries:**
- Who are my top 10 customers by revenue?
- Which customers haven't ordered in 90 days?
- Show me all purchases by ABC Corp

**Product Queries:**
- What are my best-selling products?
- Which product generated the most revenue?
- List all products from Odoo

**Invoice Queries:**
- Show me all invoices from January 2024
- What is the average invoice amount?
- Show me the highest value invoice

## Troubleshooting

### API Key Error
```
Error: ANTHROPIC_API_KEY not found
```
**Solution:** Make sure your `.env` file contains a valid API key

### Database Error
```
Error initializing database
```
**Solution:** Delete `database/sales.db` and restart the app

### Import Error
```
No module named 'streamlit'
```
**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CSV Upload Error
```
Missing required columns
```
**Solution:** Ensure your CSV has these columns:
- Customer Name
- Product Delivered (or Product Name)
- Total Invoice (or Total Amount)

## CSV Format Requirements

Your CSV should include:

| Column Name | Description | Required |
|-------------|-------------|----------|
| Customer Name | Name of customer | ✅ Yes |
| Product Delivered | Product name | ✅ Yes |
| Total Invoice | Invoice total | ✅ Yes |
| Unit Price | Price per unit | Optional |
| Quantity | Number of units | Optional |
| Invoice Date | Date of invoice | Optional |
| Invoice Number | Invoice ID | Optional |

## Next Steps

1. ✅ Import your actual sales data
2. ✅ Explore the analytics dashboard
3. ✅ Ask questions via chat
4. ✅ Share insights with your team

## Support

- Check the main [README.md](README.md) for detailed documentation
- Review the database schema in `database/schema.sql`
- See example questions in the chat interface

## Deployment

To deploy to Streamlit Cloud:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `ANTHROPIC_API_KEY` to Secrets
5. Deploy!

---

🎉 **You're all set! Happy analyzing!**
