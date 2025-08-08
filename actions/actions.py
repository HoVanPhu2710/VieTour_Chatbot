import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re

# Danh sách slug cho các tỉnh/thành Việt Nam
VN_PROVINCE_SLUGS = {
    "an giang": "an-giang", "bà rịa - vũng tàu": "ba-ria-vung-tau", "bạc liêu": "bac-lieu", "bắc kạn": "bac-kan", "bắc giang": "bac-giang", "bắc ninh": "bac-ninh", "bến tre": "ben-tre", "bình dương": "binh-duong", "bình định": "binh-dinh", "bình phước": "binh-phuoc", "bình thuận": "binh-thuan", "cà mau": "ca-mau", "cao bằng": "cao-bang", "cần thơ": "can-tho", "đà nẵng": "da-nang", "đắk lắk": "dak-lak", "đắk nông": "dak-nong", "điện biên": "dien-bien", "đồng nai": "dong-nai", "đồng tháp": "dong-thap", "gia lai": "gia-lai", "hà giang": "ha-giang", "hà nam": "ha-nam", "hà nội": "ha-noi", "hà tĩnh": "ha-tinh", "hải dương": "hai-duong", "hải phòng": "hai-phong", "hậu giang": "hau-giang", "hòa bình": "hoa-binh", "hưng yên": "hung-yen", "khánh hòa": "khanh-hoa", "kiên giang": "kien-giang", "kon tum": "kon-tum", "lai châu": "lai-chau", "lâm đồng": "lam-dong", "lạng sơn": "lang-son", "lào cai": "lao-cai", "long an": "long-an", "nam định": "nam-dinh", "nghệ an": "nghe-an", "ninh bình": "ninh-binh", "ninh thuận": "ninh-thuan", "phú thọ": "phu-tho", "phú yên": "phu-yen", "quảng bình": "quang-binh", "quảng nam": "quang-nam", "quảng ngãi": "quang-ngai", "quảng ninh": "quang-ninh", "quảng trị": "quang-tri", "sóc trăng": "soc-trang", "sơn la": "son-la", "tây ninh": "tay-ninh", "thái bình": "thai-binh", "thái nguyên": "thai-nguyen", "thanh hóa": "thanh-hoa", "thừa thiên huế": "thua-thien-hue", "tiền giang": "tien-giang", "tp hồ chí minh": "ho-chi-minh", "trà vinh": "tra-vinh", "tuyên quang": "tuyen-quang", "vĩnh long": "vinh-long", "vĩnh phúc": "vinh-phuc", "yên bái": "yen-bai"
}

class ActionGetTourBySlugOrTop(Action):
    def name(self) -> Text:
        return "action_get_tour_by_slug_or_top"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text', '').lower()
        slug = None
        # Ưu tiên search theo title nếu user hỏi 'tour <tên>'
        match = re.search(r"tour ([\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]+)", user_message)
        if match:
            search_term = match.group(1).strip()
            url = f"http://localhost:8000/api/tours?search={search_term}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tours = data.get("data", []) if isinstance(data, dict) else []
                    if isinstance(tours, list) and len(tours) > 0:
                        reply = f"Các tour liên quan đến '{search_term}':\n"
                        for tour in tours[:3]:
                            reply += f"- {tour.get('title', 'Không rõ tên')} | {tour.get('duration', '')} | {tour.get('price', 'Giá liên hệ')}\n  Link: http://localhost:5173/tour/{tour.get('slug', '')}\n  Ảnh: {tour.get('poster_url', '')}\n"
                        dispatcher.utter_message(text=reply)
                        return []
            except Exception as e:
                dispatcher.utter_message(text="Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau!")
                return []
        # Nếu user hỏi tour nổi bật, gọi luôn API top tour
        if any(kw in user_message for kw in ["nổi bật", "top", "được đặt nhiều"]):
            url = "http://localhost:8000/api/tours/top-booked?limit=3"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tours = data.get("data", []) if isinstance(data, dict) else []
                    if isinstance(tours, list) and len(tours) > 0:
                        reply = "Gợi ý các tour nổi bật:\n"
                        for tour in tours[:3]:
                            reply += f"- {tour.get('title', 'Không rõ tên')} | {tour.get('duration', '')} | {tour.get('price', 'Giá liên hệ')}\n  Link: http://localhost:5173/tour/{tour.get('slug', '')}\n  Ảnh: {tour.get('poster_url', '')}\n"
                        dispatcher.utter_message(text=reply)
                        return []
            except Exception as e:
                dispatcher.utter_message(text="Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau!")
                return []
        # Nếu không phải hỏi tour nổi bật, kiểm tra slug tỉnh thành
        for province, slug_val in VN_PROVINCE_SLUGS.items():
            if province in user_message:
                slug = slug_val
                break
        if slug:
            url = f"http://localhost:8000/api/tours?slug={slug}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tours = data.get("data", []) if isinstance(data, dict) else []
                    if isinstance(tours, list) and len(tours) > 0:
                        reply = "Các tour bạn quan tâm:\n"
                        for tour in tours[:3]:
                            reply += f"- {tour.get('title', 'Không rõ tên')} | {tour.get('duration', '')} | {tour.get('price', 'Giá liên hệ')}\n  Link: http://localhost:5173/tour/{tour.get('slug', '')}\n  Ảnh: {tour.get('poster_url', '')}\n"
                        dispatcher.utter_message(text=reply)
                        return []
            except Exception as e:
                dispatcher.utter_message(text="Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau!")
                return []
        # Nếu không có slug hoặc không tìm thấy tour, lấy top 3 tour
        url = "http://localhost:8000/api/tours/top-booked?limit=3"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tours = data.get("data", []) if isinstance(data, dict) else []
                if isinstance(tours, list) and len(tours) > 0:
                    reply = "Gợi ý các tour nổi bật:\n"
                    for tour in tours[:3]:
                        reply += f"- {tour.get('title', 'Không rõ tên')} | {tour.get('duration', '')} | {tour.get('price', 'Giá liên hệ')}\n  Link: http://localhost:5173/tour/{tour.get('slug', '')}\n  Ảnh: {tour.get('poster_url', '')}\n"
                    dispatcher.utter_message(text=reply)
                    return []
        except Exception as e:
            dispatcher.utter_message(text="Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau!")
            return []
        dispatcher.utter_message(text="Xin lỗi, hiện tại tôi không tìm thấy tour phù hợp.")
        return []