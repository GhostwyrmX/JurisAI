import React from 'react';
import { formatCitation, formatPunishment, normalizeList } from '../ipcUtils';

const BadgeList = ({ items, colorClass = 'bg-gray-100 text-gray-700' }) => {
  const values = normalizeList(items);
  if (!values.length) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {values.map((item, index) => (
        <span
          key={`${item}-${index}`}
          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${colorClass}`}
        >
          {String(item)}
        </span>
      ))}
    </div>
  );
};

const MappingList = ({ mapping }) => {
  if (!mapping || typeof mapping !== 'object') return null;

  const entries = Object.entries(mapping).filter(([, value]) => value && value !== 'not_applicable');
  if (!entries.length) return null;

  return (
    <div className="space-y-1 text-sm text-gray-700">
      {entries.map(([key, value]) => (
        <div key={key}>
          <span className="font-medium">{key.replace(/_/g, ' ')}:</span> {String(value)}
        </div>
      ))}
    </div>
  );
};

const RelatedSections = ({ relatedSections }) => {
  const values = normalizeList(relatedSections);
  if (!values.length) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {values.map((item, index) => {
        const isObject = item && typeof item === 'object';
        const label = isObject
          ? `Section ${item.section_number}${item.title ? `: ${item.title}` : ''}`
          : `Section ${item}`;

        return (
          <span
            key={`${label}-${index}`}
            className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-1 text-xs font-medium text-blue-800"
          >
            {label}
          </span>
        );
      })}
    </div>
  );
};

const LinkList = ({ links }) => {
  const values = normalizeList(links);
  if (!values.length) return null;

  return (
    <div className="space-y-2">
      {values.map((link, index) => {
        const href = typeof link === 'string' ? link : link?.url;
        const label = typeof link === 'string' ? link : (link?.title || link?.label || link?.url);

        if (!href) {
          return (
            <div key={`${label}-${index}`} className="text-sm text-gray-700">
              {label}
            </div>
          );
        }

        return (
          <a
            key={`${href}-${index}`}
            href={href}
            target="_blank"
            rel="noreferrer"
            className="block break-all text-sm text-primary-600 hover:text-primary-700 hover:underline"
          >
            {label}
          </a>
        );
      })}
    </div>
  );
};

const SectionBlock = ({ label, children }) => {
  if (!children) return null;

  return (
    <div>
      <h4 className="mb-2 text-sm font-semibold text-gray-900">{label}</h4>
      {children}
    </div>
  );
};

const IPCMetadataPanel = ({ section, compact = false }) => {
  if (!section) return null;

  const hasCrimeTypeMapping = section.crime_type_mapping && Object.values(section.crime_type_mapping).some(
    (value) => value && value !== 'not_applicable'
  );
  const hasKeywords = normalizeList(section.keywords).length > 0;
  const hasSynonyms = normalizeList(section.synonyms).length > 0;
  const hasLegalElements = normalizeList(section.legal_elements).length > 0;
  const hasExampleScenarios = normalizeList(section.example_scenarios).length > 0;
  const hasScenarioTraining = normalizeList(section.scenario_training).length > 0;
  const hasVectorSearchTerms = normalizeList(section.vector_search_terms).length > 0;
  const hasRelatedSections = normalizeList(section.related_sections).length > 0;
  const hasCourtJudgments = normalizeList(section.court_judgment_links).length > 0;

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex flex-wrap gap-2">
        {section.chapter?.chapter_name && (
          <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
            {section.chapter.chapter_name}
          </span>
        )}
        {section.crime_category && (
          <span className="inline-flex items-center rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-800">
            {section.crime_category}
          </span>
        )}
        {section.crime_subcategory && (
          <span className="inline-flex items-center rounded-full bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-800">
            {section.crime_subcategory}
          </span>
        )}
        {section.severity_level && (
          <span className="inline-flex items-center rounded-full bg-rose-100 px-2.5 py-1 text-xs font-medium text-rose-800">
            Severity: {section.severity_level}
          </span>
        )}
      </div>

      {section.description && !compact && (
        <SectionBlock label="Description">
          <p className="text-sm text-gray-700">{section.description}</p>
        </SectionBlock>
      )}

      <SectionBlock label="Citation">
        <p className="text-sm text-gray-700">{formatCitation(section.citation)}</p>
      </SectionBlock>

      <SectionBlock label="Punishment">
        <p className="text-sm text-gray-700">{formatPunishment(section.punishment)}</p>
      </SectionBlock>

      {hasCrimeTypeMapping && (
        <SectionBlock label="Crime Type Mapping">
          <MappingList mapping={section.crime_type_mapping} />
        </SectionBlock>
      )}

      {hasKeywords && (
        <SectionBlock label="Keywords">
          <BadgeList items={section.keywords} colorClass="bg-emerald-100 text-emerald-800" />
        </SectionBlock>
      )}

      {hasSynonyms && (
        <SectionBlock label="Synonyms">
          <BadgeList items={section.synonyms} colorClass="bg-cyan-100 text-cyan-800" />
        </SectionBlock>
      )}

      {!compact && (
        <>
          {hasLegalElements && (
            <SectionBlock label="Legal Elements">
              <BadgeList items={section.legal_elements} colorClass="bg-indigo-100 text-indigo-800" />
            </SectionBlock>
          )}

          {hasExampleScenarios && (
            <SectionBlock label="Example Scenarios">
              <BadgeList items={section.example_scenarios} colorClass="bg-lime-100 text-lime-800" />
            </SectionBlock>
          )}

          {hasScenarioTraining && (
            <SectionBlock label="Scenario Training">
              <BadgeList items={section.scenario_training} colorClass="bg-violet-100 text-violet-800" />
            </SectionBlock>
          )}

          {hasVectorSearchTerms && (
            <SectionBlock label="Vector Search Terms">
              <BadgeList items={section.vector_search_terms} colorClass="bg-sky-100 text-sky-800" />
            </SectionBlock>
          )}

          {hasRelatedSections && (
            <SectionBlock label="Related Sections">
              <RelatedSections relatedSections={section.related_sections} />
            </SectionBlock>
          )}

          {hasCourtJudgments && (
            <SectionBlock label="Court Judgment Links">
              <LinkList links={section.court_judgment_links} />
            </SectionBlock>
          )}
        </>
      )}
    </div>
  );
};

export default IPCMetadataPanel;
