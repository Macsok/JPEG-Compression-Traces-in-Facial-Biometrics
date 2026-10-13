# Prediction functions extracted from the notebook; comments translated into English.
import pandas as pd

def check_image(indicators, verbose=True):
    """
    Classifies an image as JFIF or PPM based on calculated indicators.

    Args:
        indicators (dict): Dictionary with calculated image indicators
        verbose (bool): Whether to display detailed information (default: True)

    Returns:
        dict: Dictionary with prediction results
    """
    if indicators is None:
        if verbose:
            print("Error: No indicators!")
        return None

    if verbose:
        print("\n           JFIF vs PPM classification")
        print("-" * 50)

    try:
        # Prepare the data for prediction
        feature_dict = {col: indicators.get(col, 0) for col in loaded_feature_columns}
        X_single = pd.DataFrame([feature_dict])

        if X_single.isnull().any().any():
            if verbose:
                print("\nMissing data in indicators:")
                print(X_single.isnull().sum()[X_single.isnull().sum() > 0])
            return None

        # Scale the features and predict
        X_single_scaled = loaded_scaler.transform(X_single)
        prediction = loaded_model.predict(X_single_scaled)[0]
        probabilities = loaded_model.predict_proba(X_single_scaled)[0]

        # Results
        if verbose:
            format_name = 'PPM (uncompressed)' if prediction == 1 else 'JFIF (JPEG compression)'
            confidence = max(probabilities) * 100
            print(f"Detected format: {format_name}")
            print(f"Confidence: {confidence:.1f}%")

        return {
            'success': True,
            'prediction': prediction,
            'format': 'PPM' if prediction == 1 else 'JFIF',
            'probabilities': {
                'JFIF': probabilities[0],
                'PPM': probabilities[1]
            },
            'confidence': max(probabilities) * 100
        }

    except Exception as e:
        if verbose:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        return None

def predict_compression_quality(indicators):
    """
    Predicts JPEG compression quality based on calculated image indicators.

    Args:
        indicators (dict): Dictionary with calculated image indicators

    Returns:
        dict: Dictionary with prediction results containing:
            - predicted_quality: predicted quality (int)
            - indicators: calculated image indicators (dict)
            - success: whether the analysis succeeded (bool)
            - error: error message (str) - only if success=False
    """
    if indicators is None:
        return {
            'success': False,
            'error': "No indicators!",
        }

    print("\n\n           Compression quality prediction")
    print("-" * 50)

    # Display the indicators used by the model (excluding estimated_quality)
    

    try:
        # Prepare the data for prediction
        feature_dict = {col: indicators.get(col, 0) for col in loaded_feature_columns
                        if col != 'estimated_quality'}
        X_single = pd.DataFrame([feature_dict])

        if X_single.isnull().any().any():
            missing = X_single.isnull().sum()[X_single.isnull().sum() > 0]
            return {
                'success': False,
                'error': f"Missing indicator data: {missing.to_dict()}",
            }

        # Predict compression quality
        predicted_quality = loaded_compression_model.predict(X_single)[0]

        # Display the result
        print(f"Predicted JPEG quality: {predicted_quality:.1f}")

        print("\n\nIndicators used by the model:")
        for key in loaded_feature_columns:
            if key in indicators and key != 'estimated_quality':
                value = indicators[key]
                if isinstance(value, (int, float)):
                    print(f"  {key:30s}: {value:>10.4f}")

        return {
            'success': True,
            'predicted_quality': predicted_quality,
            'indicators': indicators
        }

    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {
            'success': False,
            'error': error_msg
        }
