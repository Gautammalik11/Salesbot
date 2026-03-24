# Sales Data Chatbot Platform

A web-based chatbot platform to manage and analyze sales data from Odoo and Focus ERPs. Built with Streamlit and powered by Claude AI.

## Features

- 📤 **CSV Upload**: Import sales data from Odoo and Focus ERPs
- 💬 **AI Chatbot**: Ask questions about your sales data in natural language
- 📊 **Analytics Dashboard**: Visual insights and reports
- 🔍 **Smart Queries**: Automatic SQL generation from natural language
- 📈 **Visualizations**: Interactive charts and graphs

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite
- **AI**: Anthropic Claude API
- **Data Processing**: Pandas, LangChain
- **Visualization**: Plotly

## Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation

1. Clone or download this repository

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. **Upload Data**:
   - Go to "📤 Upload Data" page
   - Select your ERP source (Odoo or Focus)
   - Upload your CSV file
   - Preview and process the data

4. **Chat with Your Data**:
   - Go to "💬 Chat" page
   - Ask questions like:
     - "Show me top 10 customers by revenue"
     - "What are my best-selling products?"
     - "Total sales from Odoo vs Focus?"
     - "Which customers haven't ordered in 3 months?"

5. **View Analytics**:
   - Go to "📊 Analytics" page
   - See revenue trends, top customers, and more
   - Filter by date range and ERP source

## CSV Format

Your CSV files should include these columns (headers can vary):
- Customer Name
- Product Delivered / Product Name
- Unit Price
- Quantity
- Total Invoice / Total Amount
- Invoice Date
- Invoice Number (optional)

Example:
```csv
Customer Name,Product Delivered,Unit Price,Quantity,Total Invoice,Invoice Date,Invoice Number
ABC Corp,Widget A,10.00,50,500.00,2024-01-15,INV-001
XYZ Ltd,Widget B,25.00,20,500.00,2024-01-16,INV-002
```

## Project Structure

```
sales-chatbot/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── .env.example             # Environment variables template
├── database/
│   ├── schema.sql           # Database schema
│   └── db_manager.py        # Database operations
├── utils/
│   ├── csv_processor.py     # CSV processing
│   ├── query_engine.py      # AI query engine
│   ├── analytics.py         # Analytics functions
│   └── visualization.py     # Chart helpers
├── config/
│   └── settings.py          # Configuration
└── pages/
    ├── 1_📤_Upload_Data.py   # Upload interface
    ├── 2_💬_Chat.py          # Chat interface
    └── 3_📊_Analytics.py     # Analytics dashboard
```

## Deployment

### Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add your `ANTHROPIC_API_KEY` to Secrets
5. Deploy!

**Cost**: Free tier available, or $20/month for private apps

## Troubleshooting

**Database locked error**:
- Close all other connections to the database
- Restart the application

**API key error**:
- Check your `.env` file has the correct API key
- Ensure the key starts with `sk-ant-`

**CSV upload fails**:
- Check your CSV has required columns
- Ensure date format is YYYY-MM-DD or MM/DD/YYYY
- Remove special characters from headers

## Support

For issues or questions, please check:
- Streamlit docs: https://docs.streamlit.io
- LangChain docs: https://docs.langchain.com
- Anthropic docs: https://docs.anthropic.com

## License

MIT License - feel free to use and modify for your needs!
