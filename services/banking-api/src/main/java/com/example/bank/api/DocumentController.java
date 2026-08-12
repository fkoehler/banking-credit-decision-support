package com.example.bank.api;

import jakarta.validation.Valid;
import java.util.Arrays;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/documents")
public class DocumentController {
    private final AiClient aiClient;

    DocumentController(AiClient aiClient) {
        this.aiClient = aiClient;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    ApiModels.DocumentResponse ingest(@Valid @RequestBody ApiModels.DocumentRequest request) {
        String source = request.source() == null || request.source().isBlank() ? "synthetic" : request.source();
        return aiClient.ingest(new ApiModels.DocumentRequest(request.title(), request.content(), source));
    }

    @GetMapping
    List<ApiModels.DocumentSummary> list() {
        ApiModels.DocumentSummary[] documents = aiClient.listDocuments();
        return documents == null ? List.of() : Arrays.asList(documents);
    }
}
