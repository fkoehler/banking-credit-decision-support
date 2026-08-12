package com.example.bank.api;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

@Configuration
@EnableMethodSecurity
public class SecurityConfiguration {
    @Bean
    @ConditionalOnProperty(name = "app.auth-mode", havingValue = "local", matchIfMissing = true)
    UserDetailsService localUsers(
        @Value("${app.local-users.advisor.username}") String advisorUsername,
        @Value("${app.local-users.advisor.password}") String advisorPassword,
        @Value("${app.local-users.reviewer.username}") String reviewerUsername,
        @Value("${app.local-users.reviewer.password}") String reviewerPassword
    ) {
        return new InMemoryUserDetailsManager(
            User.withUsername(advisorUsername).password("{noop}" + advisorPassword).roles("ADVISOR").build(),
            User.withUsername(reviewerUsername).password("{noop}" + reviewerPassword).roles("RISK_REVIEWER").build()
        );
    }

    @Bean
    @ConditionalOnProperty(name = "app.auth-mode", havingValue = "local", matchIfMissing = true)
    SecurityFilterChain localSecurity(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .cors(Customizer.withDefaults())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/api/v1/cases/*/decisions", "/api/v1/documents/**").hasRole("RISK_REVIEWER")
                .anyRequest().authenticated())
            .httpBasic(Customizer.withDefaults())
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "app.auth-mode", havingValue = "oidc")
    SecurityFilterChain oidcSecurity(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .cors(Customizer.withDefaults())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/api/v1/cases/*/decisions", "/api/v1/documents/**").hasRole("RISK_REVIEWER")
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth -> oauth.jwt(Customizer.withDefaults()))
            .build();
    }

    @Bean
    CorsConfigurationSource corsConfigurationSource(@Value("${app.web-origin}") String webOrigin) {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.addAllowedOrigin(webOrigin);
        configuration.addAllowedHeader("*");
        configuration.addAllowedMethod("*");
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}

