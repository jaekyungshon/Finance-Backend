package com.capstone.finance.Controller;



import com.capstone.finance.Service.CompanyInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/price-menu/res")
public class CompanyInfoController {
    @Autowired
    private CompanyInfoService companyInfoService;

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> fetchPrices() {
        List<Object[]> data = companyInfoService.getLatestDailyChartData();

        List<Map<String, Object>> result = data.stream().map(entry -> Map.of(
                "code", entry[0],
                "date", entry[1],
                "company", entry[2],
                "open", entry[3],
                "close", entry[4],
                "volume", entry[5]
        )).collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }

    @GetMapping("/req")
    public ResponseEntity<List<Map<String, Object>>> searchPrices(@RequestParam String search) {
        List<Object[]> data = companyInfoService.searchStockData(search);

        List<Map<String, Object>> result = data.stream().map(entry -> Map.of(
                "code", entry[0],
                "date", entry[1],
                "company", entry[2],
                "open", entry[3],
                "close", entry[4],
                "volume", entry[5]
        )).collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }
}
