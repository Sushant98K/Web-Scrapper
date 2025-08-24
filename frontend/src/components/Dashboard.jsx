import { useState, useEffect } from "react";
import { RefreshCw, Clock, ExternalLink, AlertCircle } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://0.0.0.0:8000";

const Dashboard = () => {
  const [scrapedData, setScrapedData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [sourceType, setSourceType] = useState("news");

  const fetchData = async (type = sourceType) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_URL}/scrape/${type}`);
      if (response.data.success) {
        setScrapedData(response.data.data);
        setLastUpdated(new Date().toLocaleString());
        setSourceType(type);

        setError(null)
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(
        "Failed to fetch data. Make sure the backend server is running."
      );
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData("news");
  }, []);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-serif font-bold text-foreground mb-2">
            Dashboard
          </h1>
          <p className="text-muted-foreground">
            Latest scraped data from selected source
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 mt-4 sm:mt-0">
          {/* Source Switch Buttons */}
          <button
            onClick={() => fetchData("news")}
            className={`px-3 py-1 rounded-md ${
              sourceType === "news"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            News
          </button>
          <button
            onClick={() => fetchData("quotes")}
            className={`px-3 py-1 rounded-md ${
              sourceType === "quotes"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            Quotes
          </button>

          {lastUpdated && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>Last updated: {lastUpdated}</span>
            </div>
          )}

          <button
            onClick={() => fetchData(sourceType)}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Fetching..." : "Refresh Data"}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Items
              </p>
              <p className="text-2xl font-bold text-foreground">
                {scrapedData.length}
              </p>
            </div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <RefreshCw className="h-6 w-6 text-primary" />
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Status
              </p>
              <p className="text-2xl font-bold text-foreground">
                {loading ? "Loading" : error ? "Error" : "Active"}
              </p>
            </div>
            <div
              className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                loading
                  ? "bg-secondary/10"
                  : error
                  ? "bg-destructive/10"
                  : "bg-accent/10"
              }`}
            >
              <div
                className={`w-3 h-3 rounded-full ${
                  loading
                    ? "bg-secondary animate-pulse"
                    : error
                    ? "bg-destructive"
                    : "bg-accent"
                }`}
              />
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Source
              </p>
              <p className="text-2xl font-bold text-foreground capitalize">
                {sourceType}
              </p>
            </div>
            <a
              href={
                sourceType === "news"
                  ? "https://news.ycombinator.com/"
                  : "https://quotes.toscrape.com/"
              }
              target="_blank"
              rel="noopener noreferrer"
              className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center"
            >
              <ExternalLink className="h-6 w-6 text-accent" />
            </a>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <p className="text-destructive font-medium">Error</p>
          </div>
          <p className="text-destructive/80 mt-1">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && scrapedData.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <div
              key={index}
              className="bg-card p-6 rounded-lg border border-border animate-pulse"
            >
              <div className="h-4 bg-muted rounded w-3/4 mb-3"></div>
              <div className="h-3 bg-muted rounded w-full mb-2"></div>
              <div className="h-3 bg-muted rounded w-2/3 mb-4"></div>
              <div className="h-3 bg-muted rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}

      {/* Data Grid */}
      {!loading && scrapedData.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scrapedData.map((item, index) => (
            <div
              key={index}
              className="bg-card p-6 rounded-lg border border-border hover:shadow-md transition-shadow"
            >
              <h3 className="font-serif font-semibold text-foreground mb-3 line-clamp-2">
                {item.title}
              </h3>

              {item.description && (
                <p className="text-muted-foreground text-sm mb-4 line-clamp-3">
                  {item.description}
                </p>
              )}

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{formatTimestamp(item.timestamp)}</span>
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-primary hover:text-primary/80 transition-colors"
                  >
                    <ExternalLink className="h-3 w-3" />
                    Read more
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && scrapedData.length === 0 && (
        <div className="text-center py-12">
          <RefreshCw className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-serif font-semibold text-foreground mb-2">
            No data available
          </h3>
          <p className="text-muted-foreground mb-4">
            Click the refresh button to fetch the latest data
          </p>
          <button
            onClick={() => fetchData(sourceType)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Fetch Data
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
