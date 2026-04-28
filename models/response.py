from flask import jsonify, send_file


def success_response(data=None, message="Success", status_code=200):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), status_code


def error_response(message="Something went wrong", status_code=400, errors=None):
    return jsonify({
        "status": "error",
        "message": message,
        "errors": errors
    }), status_code


def file_response(file_obj, filename, mimetype, message="Success", status_code=200):
    response = send_file(
        file_obj,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )

    response.headers["X-Status"] = "success"
    response.headers["X-Message"] = message

    return response, status_code