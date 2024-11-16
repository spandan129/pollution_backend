from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

def test_history_data_endpoint(capsys):
    url = "/api/history-data"
    params = {"start_date": "2023-01-01", "end_date": "2023-01-05"}

    response = client.get(url, params=params)

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total_items" in data
    assert "start_date" in data
    assert "end_date" in data

    for item in data["items"]:
        assert "date" in item
        assert "id" in item
        assert "air_quality_index" in item
        assert "ph_level" in item
        assert "water_quality_index" in item
        assert "temperature" in item

    assert data["total_items"] == 5
    assert data["start_date"] == "2023-01-01"
    assert data["end_date"] == "2023-01-05"

    print("History data endpoint test passed successfully!")

    captured = capsys.readouterr()
    assert "History data endpoint test passed successfully!" in captured.out

def test_get_all_data_of_pollution_endpoint(capsys):  
    url = "/api/get_all_data_of_pollution"
    params = {"start_date": "2023-01-01", "end_date": "2023-01-05"}

    response = client.get(url, params=params)

    assert response.status_code == 200
    data = response.json()

    assert "historical_data" in data
    assert "live_sensor_data" in data
    assert "weather_data" in data

    historical_data = data["historical_data"]
    assert "items" in historical_data
    assert "total_items" in historical_data
    assert "start_date" in historical_data
    assert "end_date" in historical_data

    live_sensor_data = data["live_sensor_data"]
    assert "sensor_id" in live_sensor_data
    assert "timestamp" in live_sensor_data
    assert "air_quality_index" in live_sensor_data
    assert "ph_level" in live_sensor_data
    assert "water_quality_index" in live_sensor_data

    weather_data = data["weather_data"]
    assert "coord" in weather_data
    assert "weather" in weather_data
    assert "main" in weather_data
    assert "wind" in weather_data
    assert "clouds" in weather_data
    assert "sys" in weather_data

    assert historical_data["total_items"] == 5
    assert historical_data["start_date"] == "2023-01-01"
    assert historical_data["end_date"] == "2023-01-05"

    print("Get all data of pollution endpoint test passed successfully!")

    captured = capsys.readouterr()
    assert "Get all data of pollution endpoint test passed successfully!" in captured.out
