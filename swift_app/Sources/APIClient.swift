import Foundation

class APIClient {
    static let shared = APIClient()
    private let baseURL = "http://127.0.0.1:8000/api"
    
    func convertFile(path: String, completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "\(baseURL)/convert") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "source_type": "file",
            "source": path
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("API Error: \(error.localizedDescription)")
                completion(false)
                return
            }
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                completion(true)
            } else {
                completion(false)
            }
        }
        task.resume()
    }
    
    struct Document: Codable {
        let name: String
        let path: String
    }
    
    func listKnowledgeBase(completion: @escaping ([Document]) -> Void) {
        guard let url = URL(string: "\(baseURL)/kb/list") else { return }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            guard let data = data, error == nil else {
                completion([])
                return
            }
            struct ResponseData: Codable {
                let status: String
                let documents: [Document]
            }
            if let decoded = try? JSONDecoder().decode(ResponseData.self, from: data) {
                completion(decoded.documents)
            } else {
                completion([])
            }
        }
        task.resume()
    }
    
    func deleteDocument(path: String, completion: @escaping (Bool) -> Void) {
        guard let encodedPath = path.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let url = URL(string: "\(baseURL)/kb/delete?file_path=\(encodedPath)") else {
            completion(false)
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("API Delete Error: \(error.localizedDescription)")
                completion(false)
                return
            }
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                completion(true)
            } else {
                completion(false)
            }
        }
        task.resume()
    }
    
    func chat(prompt: String, useRAG: Bool, history: [[String: String]] = [], completion: @escaping (String?) -> Void) {
        guard let url = URL(string: "\(baseURL)/chat") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "prompt": prompt,
            "history": history,
            "use_rag": useRAG
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, error == nil else {
                completion(nil)
                return
            }
            struct ResponseData: Codable {
                let status: String
                let response: String
            }
            if let decoded = try? JSONDecoder().decode(ResponseData.self, from: data) {
                completion(decoded.response)
            } else {
                completion(nil)
            }
        }
        task.resume()
    }
}
